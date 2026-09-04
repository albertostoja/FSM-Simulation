from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fsm_mzi_sim import (
    BeamConfig,
    DetectorConfig,
    FSMJitterConfig,
    FSMTone,
    InterferometerConfig,
    PolarizationConfig,
    plot_diagnostics,
    plot_quadrature,
    simulate_fsm_motion,
    simulate_quadrature,
)


def main() -> None:
    beam = BeamConfig(
        wavelength_m=633e-9,
        radius_at_output_aperture_m=0.5e-3,
        distance_output_aperture_to_fsm_m=0.75,
        divergence_half_angle_rad=0.35e-3,
    )
    interferometer = InterferometerConfig(
        distance_fsm_to_combiner_m=0.35,
        fsm_incidence_angle_rad=0.7853981633974483,
        baseline_visibility=0.96,
        nominal_phase_rad=0.25,
        quadrature_phase_rad=1.5707963267948966,
        fsm_vertical_pivot_offset_m=0.8e-3,
        piston_shear_axis="horizontal",
        include_piston_opd=True,
        include_piston_shear=True,
    )
    detector = DetectorConfig(
        vertical_gain=1.0,
        horizontal_gain=0.96,
        horizontal_offset_w=0.015,
        read_noise_std_w=0.003,
    )
    polarization = PolarizationConfig(
        reference_hwp_fast_axis_angle_rad=0.39269908169872414,
        fsm_qwp_fast_axis_angle_rad=0.7853981633974483,
    )
    jitter = FSMJitterConfig(
        sample_rate_hz=50_000,
        duration_s=0.04,
        vertical_steering_rms_rad=0.7e-6,
        horizontal_steering_rms_rad=0.45e-6,
        piston_rms_m=35e-9,
        correlation_time_s=80e-6,
        tones=(
            FSMTone(
                frequency_hz=650,
                vertical_steering_amplitude_rad=1.8e-6,
                piston_amplitude_m=45e-9,
            ),
            FSMTone(
                frequency_hz=2100,
                horizontal_steering_amplitude_rad=0.75e-6,
                piston_phase_rad=1.2,
            ),
        ),
        seed=11,
    )

    motion = simulate_fsm_motion(jitter)
    result = simulate_quadrature(
        motion,
        beam,
        interferometer,
        detector,
        polarization=polarization,
        noise_seed=23,
    )

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    figure_path = output_dir / "quadrature_demo.png"

    fig = plt.figure(figsize=(11, 8.5), constrained_layout=True)
    grid = fig.add_gridspec(4, 2, width_ratios=[1.05, 1.35])
    ax_quad = fig.add_subplot(grid[:, 0])
    plot_quadrature(result, ax=ax_quad, color_by="time", point_size=5)

    diagnostic_axes = []
    for row in range(4):
        sharex = diagnostic_axes[0] if diagnostic_axes else None
        diagnostic_axes.append(fig.add_subplot(grid[row, 1], sharex=sharex))
    plot_diagnostics(result, axes=diagnostic_axes)
    fig.savefig(figure_path, dpi=160)
    plt.close(fig)

    print(f"Wrote {figure_path}")
    print(f"Mean visibility: {result.visibility.mean():.4f}")
    print(f"Beam radius at combiner: {result.beam_radius_at_combiner_m * 1e3:.3f} mm")


if __name__ == "__main__":
    main()
