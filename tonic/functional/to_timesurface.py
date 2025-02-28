import numpy as np

def to_timesurface_numpy(
    events,
    sensor_size,
    ordering,
    surface_dimensions=(7, 7),
    tau=5e3,
    decay="lin",
    merge_polarities=False,
):
    """Representation that creates timesurfaces for each event in the recording. Modeled after the paper
    Lagorce et al. 2016, Hots: a hierarchy of event-based time-surfaces for pattern recognition
    https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=7508476

    Parameters:
        surface_dimensions (int, int): width does not have to be equal to height, however both numbers have to be odd.
            if surface_dimensions is None: the time surface is defined globally, on the whole sensor grid.
        tau (float): time constant to decay events around occuring event with.
        decay (str): can be either 'lin' or 'exp', corresponding to linear or exponential decay.
        merge_polarities (bool): flag that tells whether polarities should be taken into account separately or not.

    Returns:
        array of timesurfaces with dimensions (w,h) or (p,w,h)
    """
    if surface_dimensions:
        radius_x = surface_dimensions[0] // 2
        radius_y = surface_dimensions[1] // 2
    else:
        radius_x = 0
        radius_y = 0
        surface_dimensions = sensor_size
        
    assert "x" and "y" and "t" and "p" in ordering
    x_index = ordering.find("x")
    y_index = ordering.find("y")
    t_index = ordering.find("t")
    p_index = ordering.find("p")
    n_of_events = len(events)

    if merge_polarities:
        events[:, p_index] = np.zeros(n_of_events)
    n_of_pols = len(np.unique(events[:, p_index]))
    timestamp_memory = np.zeros(
        (n_of_pols, sensor_size[0] + radius_x * 2, sensor_size[1] + radius_y * 2)
    )
    timestamp_memory -= tau * 3 + 1
    all_surfaces = np.zeros(
        (n_of_events, n_of_pols, surface_dimensions[0], surface_dimensions[1])
    )
    for index, event in enumerate(events):
        x = int(event[x_index])
        y = int(event[y_index])
        timestamp_memory[int(event[p_index]), x + radius_x, y + radius_y] = event[
            t_index
        ]
        if radius_x > 0 and radius_y > 0:
            timestamp_context = (
                timestamp_memory[
                    :, x : x + surface_dimensions[0], y : y + surface_dimensions[1]
                ]
                - event[t_index]
            )
        else:
            timestamp_context = (timestamp_memory - event[t_index])
            
        if decay == "lin":
            timesurface = timestamp_context / (3 * tau) + 1
            timesurface[timesurface < 0] = 0
        elif decay == "exp":
            timesurface = np.exp(timestamp_context / tau)
            timesurface[timestamp_context < (-3 * tau)] = 0
        all_surfaces[index, :, :, :] = timesurface
    return all_surfaces
