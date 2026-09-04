# FSM Quadrature MZI Simulation

This project simulates a quadrature-channel Mach-Zehnder interferometer where one
mirror is a fast-steering mirror (FSM). The main output is a plot of vertical
polarization photodiode intensity versus horizontal polarization photodiode
intensity.

The attached diagram is treated as visual context for the setup. The simulation
code is driven by the parameter objects in `fsm_mzi_sim`, not by any text in the
image.

## What Is Modeled

The model combines three effects:

1. Quadrature interference:
   - Vertical channel: `I_v = 0.5 P (1 + V cos(phi))`
   - Horizontal channel: `I_h = 0.5 P (1 + V cos(phi + q))`
   - `q = pi/2` gives ideal quadrature.

2. FSM angular motion:
   - A mirror angle change sends the reflected beam by twice that angle.
   - The angular deflection creates lateral shear at the recombining beamsplitter.
   - Angular mismatch and shear reduce Gaussian mode overlap, which reduces
     fringe visibility.

3. FSM piston motion:
   - Physical mirror-normal piston changes optical path difference by
     `2 * piston * cos(fsm_incidence_angle_rad)`.
   - For non-normal incidence, the same piston creates lateral beam walk of
     `2 * piston * sin(fsm_incidence_angle_rad)`.
   - Piston-induced beam walk is included in Gaussian mode overlap, so it can
     reduce fringe visibility and pull quadrature points inward.
   - Optional pivot-offset terms convert mirror steering into path length.
   - An optional small geometric path term from beam angle is included.

4. Reference mirror tap:
   - A sinusoidal linear displacement in the non-FSM arm can be used to sweep
     OPD and generate the clean quadrature circle seen in bench alignment.
   - By default, the displacement points toward the combiner and only changes
     OPD. Optional horizontal/vertical direction angles add a small beam walk
     component to mimic imperfect tapping or mounting geometry.

5. Optional Jones-vector polarization optics:
   - With `PolarizationConfig`, the vertical and horizontal photodiodes are
     computed from the H/V components of the recombined electric field.
   - The default is a vertically polarized laser, a reference-arm HWP fast axis
     at 22.5 degrees, and an FSM-arm QWP fast axis at 45 degrees.
   - Rotating either waveplate changes the channel centers, contrast, ellipse
     shape, and relative phase.

The output is intentionally configurable rather than pretending to know every
detail of the bench. You can replace the synthetic jitter with measured FSM
time-series data by constructing an `FSMMotion` directly. In `FSMMotion`,
`piston_m` is physical mirror-normal motion; if you have measured OPD instead,
convert using `piston = OPD / (2 * cos(fsm_incidence_angle_rad))`.

## Quick Start

```powershell
python -m pip install -e .
python .\examples\basic_simulation.py
```

The example writes a demo figure to `outputs/quadrature_demo.png`.

To work interactively:

```powershell
jupyter notebook .\notebooks\quadrature_fsm_simulation.ipynb
```

The notebook includes a "Beam Walk At The Combiner" section that treats the
recombining beamsplitter plane as a stationary quadcell-like cross-section. It
plots the relative beam-center displacement between the two arms in horizontal
and vertical physical space before showing the quadrature-channel intensity
plot.

The deterministic FSM example section can also generate GIFs in `outputs/`.
Each animation evolves the beam walk, quadrature trace, and inferred OPD over
time.

## Main Parameters

- `BeamConfig.wavelength_m`: laser wavelength.
- `BeamConfig.radius_at_output_aperture_m`: 1/e^2 intensity radius at the
  laser output aperture. If a listed beam size is a diameter, use half that
  value here.
- `BeamConfig.distance_output_aperture_to_fsm_m`: distance from the laser
  output aperture to the FSM.
- `BeamConfig.radius_at_fsm_effective_m`: computed 1/e^2 intensity radius at
  the FSM.
- `BeamConfig.radius_at_fsm_m`: legacy direct 1/e^2 intensity radius at the
  FSM, used only when `radius_at_output_aperture_m` is not set.
- `BeamConfig.divergence_half_angle_rad`: beam-radius growth per meter,
  interpreted as the half-angle divergence.
- `InterferometerConfig.distance_fsm_to_combiner_m`: FSM to recombining
  beamsplitter distance.
- `InterferometerConfig.fsm_incidence_angle_rad`: angle between the incoming
  beam and the FSM surface normal. A 45 degree fold mirror uses `pi / 4`.
- `InterferometerConfig.piston_shear_axis`: whether piston-induced beam walk is
  added to the horizontal or vertical shear direction.
- `InterferometerConfig.baseline_visibility`: static visibility before FSM
  mismatch effects.
- `InterferometerConfig.quadrature_phase_rad`: channel phase offset, usually
  `pi/2`. This is used by the older ideal-channel model when no
  `PolarizationConfig` is supplied.
- `FSMJitterConfig.vertical_steering_rms_rad`: mirror angular jitter RMS that
  steers the reflected beam up/down out of the optical-table plane.
- `FSMJitterConfig.horizontal_steering_rms_rad`: mirror angular jitter RMS that
  steers the reflected beam left/right within the optical-table plane.
- `FSMJitterConfig.piston_rms_m`: surface piston jitter RMS.
- `ReferenceMirrorTapConfig.amplitude_m`: sinusoidal tap displacement amplitude
  for sweeping OPD in the non-FSM arm.
- `ReferenceMirrorTapConfig.opd_coupling`: OPD change per meter of longitudinal
  tapped-mirror displacement.
- `PolarizationConfig.reference_hwp_fast_axis_angle_rad`: HWP fast-axis angle in
  the non-FSM arm, measured from vertical. Use 22.5 degrees to rotate vertical
  input light into 45 degree diagonal linear polarization.
- `PolarizationConfig.fsm_qwp_fast_axis_angle_rad`: QWP fast-axis angle in the
  FSM arm, measured from vertical. The default 45 degrees gives circular
  polarization from vertical input light.
- `PolarizationConfig.reference_hwp_retardance_rad` and
  `PolarizationConfig.fsm_qwp_retardance_rad`: ideal values are `pi` and
  `pi/2`; changing them can mimic imperfect retardance.
- `DetectorConfig`: channel gains, offsets, contrast, and detector noise.

All distances are meters, angles are radians, and powers are arbitrary linear
units unless you choose to calibrate `input_power_w`.
