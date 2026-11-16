# Aerospace review checklist

## Units and frames
- [ ] Every physical quantity at an interface has a stated unit (a type, a name suffix, or a doc comment).
- [ ] No implicit mixing of units (ft vs m, kts vs m/s, deg vs rad, lbf vs N).
- [ ] Every vector names its reference frame (ECI, ECEF, NED, ENU, body), and transforms are explicit and tested.
- [ ] The angle convention (Euler order, quaternion scalar-first or scalar-last, handedness) is documented and consistent.
- [ ] Time scales (UTC, TAI, GPS, TT) and epochs are explicit. Leap seconds are handled where relevant.

## Numerics
- [ ] Floating-point equality isn't used for physical values. Tolerances are justified.
- [ ] Singularities are handled (gimbal lock, division by small airspeed or altitude, poles in lat/lon).
- [ ] Integrator step size and stability are justified for the dynamics' stiffness.
- [ ] Angles are wrapped and normalised consistently (−π..π or 0..2π, as documented).
- [ ] Quaternions are renormalised, and the sign ambiguity is handled.
- [ ] Accumulation error over long runs is bounded or tested.

## Envelope and failure modes
- [ ] The valid operating envelope is defined, and inputs outside it are detected and handled.
- [ ] Sensor dropout, stale data and NaN propagation are handled, with defined fallback behaviour.
- [ ] Rate and magnitude limits (actuator saturation, rate limits) are modelled and tested.
- [ ] Safety margins are stated, with their source.

## Verification
- [ ] Tests compare against independent references: analytic solutions, published data, or conservation laws.
- [ ] Every requirement maps to a test (AC ids in test names; `builtin:trace` passes).
- [ ] Determinism: fixed seeds, fixed step sizes, and platform-independent results within tolerance.
- [ ] If DO-178C or ARP4754 objectives apply, the human has been told about the coverage criteria (statement, decision, MC/DC) required for the assurance level.
