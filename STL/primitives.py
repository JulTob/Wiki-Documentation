"""Sphere, point-marker and arrow meshes in one coordinate system.

Lengths are model coordinates. A point marker's size is a display choice,
and an arrow's endpoints are spatial positions, not unscaled field values.
"""

from __future__ import annotations

import math

from mesh_tools import (
    Mesh,
    Vector,
    check_mesh,
    cross,
    length,
    subtract,
    unit,
    )


def _position(value: Vector, name: str) -> Vector:
    try:
        coordinates = tuple( float( component ) for component in value )
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError( f'{name} needs three finite coordinates.' ) from error

    if (
        len( coordinates ) != 3
        or not all( math.isfinite( component ) for component in coordinates )
        ):
        raise ValueError( f'{name} needs three finite coordinates.' )

    return coordinates


def _positive(value: float, name: str) -> float:
    try:
        value = float( value )
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError( f'{name} must be finite and positive.' ) from error

    if not math.isfinite( value ) or value <= 0:
        raise ValueError( f'{name} must be finite and positive.' )
    return value


def _subdivisions(value: int, name: str) -> None:
    if type( value ) is not int or value < 3:
        raise ValueError( f'{name} must be an integer of at least three.' )


def _closed_mesh(
        vertices: list[Vector],
        faces: list[tuple[int, int, int]],
        ) -> Mesh:
    mesh = Mesh(
            tuple( vertices ),
            tuple( faces ),
            )
    check_mesh(
            mesh,
            closed=True,
            )
    return mesh


def _transverse_frame(axis: Vector) -> tuple[Vector, Vector]:
    # Ties use the first world axis. Roll can jump at reference changes.
    reference_index = min(
            range( 3 ),
            key=lambda index: abs( axis[ index ] ),
            )
    reference = tuple(
        1.0 if index == reference_index else 0.0
        for index in range( 3 )
        )
    lateral = unit( cross( axis, reference ) )
    transverse = cross( axis, lateral )
    return lateral, transverse


def sphere_mesh(
        radius: float,
        latitude_steps: int = 32,
        longitude_steps: int = 64,
        *,
        centre: Vector = (0.0, 0.0, 0.0),
        ) -> Mesh:
    """Return a closed, outward-wound sphere approximation.

    Radius is positive; subdivisions are integers >=3; centre is finite.
    The default has 3,968 triangles. Planar facets approximate the sphere.
    Invalid or numerically unresolved geometry raises ValueError.
    """
    radius = _positive( radius, 'Radius' )
    centre = _position( centre, 'Centre' )
    _subdivisions( latitude_steps, 'Latitude steps' )
    _subdivisions( longitude_steps, 'Longitude steps' )

    def at_offset(x: float, y: float, z: float) -> Vector:
        return (
            centre[ 0 ] + x,
            centre[ 1 ] + y,
            centre[ 2 ] + z,
            )

    vertices = [at_offset( 0.0, 0.0, radius )]
    for latitude in range( 1, latitude_steps ):
        theta = math.pi * latitude / latitude_steps
        for longitude in range( longitude_steps ):
            phi = 2 * math.pi * longitude / longitude_steps
            vertices.append(
                    at_offset(
                            radius * math.sin( theta ) * math.cos( phi ),
                            radius * math.sin( theta ) * math.sin( phi ),
                            radius * math.cos( theta ),
                            ),
                    )
    south = len( vertices )
    vertices.append( at_offset( 0.0, 0.0, -radius ) )

    def ring(latitude: int, longitude: int) -> int:
        return 1 + latitude * longitude_steps + longitude % longitude_steps

    faces = []
    for longitude in range( longitude_steps ):
        faces.append(
                (
                    0,
                    ring( 0, longitude ),
                    ring( 0, longitude + 1 ),
                    ),
                )
        for latitude in range( latitude_steps - 2 ):
            upper = ring( latitude, longitude )
            upper_next = ring( latitude, longitude + 1 )
            lower = ring( latitude + 1, longitude )
            lower_next = ring( latitude + 1, longitude + 1 )
            faces.extend(
                    (
                        (upper, lower, lower_next),
                        (upper, lower_next, upper_next),
                        ),
                    )
        faces.append(
                (
                    ring( latitude_steps - 2, longitude ),
                    south,
                    ring( latitude_steps - 2, longitude + 1 ),
                    ),
                )

    return _closed_mesh( vertices, faces )


def point_mesh(
        position: Vector,
        marker_radius: float,
        *,
        latitude_steps: int = 16,
        longitude_steps: int = 32,
        ) -> Mesh:
    """Mark a finite spatial point with a small sphere of positive radius.

    The radius conveys visibility, not uncertainty or physical size unless
    the figure explicitly assigns it that meaning. It scales with the view;
    it is not a fixed-pixel billboard.
    """
    return sphere_mesh(
            marker_radius,
            latitude_steps,
            longitude_steps,
            centre=position,
            )


def cube_point_mesh(
        position: Vector,
        marker_size: float,
        ) -> Mesh:
    """Return a world-axis-aligned cube centred at a finite position.

    Marker size is the finite positive full side length in model units,
    a display choice rather than physical size or uncertainty. The closed
    cube has eight vertices and twelve outward triangles. Invalid or
    numerically unresolved geometry raises ValueError.
    """
    position = _position( position, 'Position' )
    marker_size = _positive( marker_size, 'Marker size' )
    half_side = marker_size / 2
    vertices = [
        tuple(
            coordinate + sign * half_side
            for coordinate, sign in zip( position, signs )
            )
        for signs in (
                (-1, -1, -1),
                (1, -1, -1),
                (1, 1, -1),
                (-1, 1, -1),
                (-1, -1, 1),
                (1, -1, 1),
                (1, 1, 1),
                (-1, 1, 1),
                )
        ]
    faces = []
    for first, second, third, fourth in (
            (0, 3, 2, 1),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
            ):
        faces.extend(
                (
                    (first, second, third),
                    (first, third, fourth),
                    ),
                )

    return _closed_mesh( vertices, faces )


def arrow_mesh(
        start: Vector,
        end: Vector,
        *,
        shaft_radius: float | None = None,
        head_radius: float | None = None,
        head_length: float | None = None,
        sides: int = 24,
        ) -> Mesh:
    """Return a closed shaft-and-cone arrow from start to distinct end.

    Endpoints are finite spatial positions. Widths are positive, head radius
    exceeds shaft radius, and 0<head length<arrow length. Default widths and
    head length scale with arrow length. The vector is end-start; a field
    value needs an explicit conversion to display displacement beforehand.
    """
    start = _position( start, 'Start' )
    end = _position( end, 'End' )
    _subdivisions( sides, 'Sides' )
    displacement = subtract( end, start )
    distance = _positive( length( displacement ), 'Arrow length' )
    axis = unit( displacement )

    shaft_radius = _positive(
            0.02 * distance if shaft_radius is None else shaft_radius,
            'Shaft radius',
            )
    head_radius = _positive(
            0.06 * distance if head_radius is None else head_radius,
            'Head radius',
            )
    head_length = _positive(
            0.22 * distance if head_length is None else head_length,
            'Head length',
            )
    if head_radius <= shaft_radius:
        raise ValueError( 'Head radius must exceed shaft radius.' )
    if head_length >= distance:
        raise ValueError( 'Head length must be shorter than the arrow.' )

    lateral, transverse = _transverse_frame( axis )

    vertices = []
    ring_specs = (
        (0.0, shaft_radius),
        (distance - head_length, shaft_radius),
        (distance - head_length, head_radius),
        )
    for axial_distance, radius in ring_specs:
        for index in range( sides ):
            angle = 2 * math.pi * index / sides
            vertex = tuple(
                start[ coordinate ]
                + axial_distance * axis[ coordinate ]
                + radius * (
                    math.cos( angle ) * lateral[ coordinate ]
                    + math.sin( angle ) * transverse[ coordinate ]
                    )
                for coordinate in range( 3 )
                )
            vertices.append( vertex )

    tail = len( vertices )
    vertices.append( start )
    tip = len( vertices )
    vertices.append( end )
    faces = []
    for index in range( sides ):
        following = (index + 1) % sides
        neck = sides + index
        next_neck = sides + following
        head = 2 * sides + index
        next_head = 2 * sides + following
        faces.extend(
                (
                    (tail, following, index),
                    (index, following, next_neck),
                    (index, next_neck, neck),
                    (neck, next_neck, next_head),
                    (neck, next_head, head),
                    (head, next_head, tip),
                    ),
                )

    return _closed_mesh( vertices, faces )


def crossed_pyramid_arrow_mesh(
        start: Vector,
        end: Vector,
        *,
        head_width: float | None = None,
        head_length: float | None = None,
        ) -> Mesh:
    """Return an open six-triangle display arrow from start to distinct end.

    Endpoints are finite positions. Head width is the full square side,
    default 0.12 times arrow length; head length defaults to 0.22 times it.
    Sizes are finite positive, with head length shorter than the arrow.
    Four pyramid sides have no base cap. Two opposite-corner tail triangles
    intentionally intersect along the axis: this is not a closed solid.

    Intended side-view coverage requires destination two-sided rendering,
    which is not verified by this constructor or encoded as an STL option.
    Both filled fins vanish end-on. Roll uses the least-aligned world axis,
    first coordinate on ties, and can jump when that reference changes.
    Invalid or numerically unresolved geometry raises ValueError.
    """
    start = _position( start, 'Start' )
    end = _position( end, 'End' )
    displacement = subtract( end, start )
    distance = _positive( length( displacement ), 'Arrow length' )
    axis = unit( displacement )
    lateral, transverse = _transverse_frame( axis )

    head_width = _positive(
            0.12 * distance if head_width is None else head_width,
            'Head width',
            )
    head_length = _positive(
            0.22 * distance if head_length is None else head_length,
            'Head length',
            )
    if head_length >= distance:
        raise ValueError( 'Head length must be shorter than the arrow.' )

    base_centre = tuple(
        end[ coordinate ] - head_length * axis[ coordinate ]
        for coordinate in range( 3 )
        )
    if base_centre == end:
        raise ValueError(
                'Head length is numerically unresolved at these coordinates.',
                )
    half_width = head_width / 2
    vertices = [
        tuple(
            base_centre[ coordinate ]
            + half_width * (
                lateral_sign * lateral[ coordinate ]
                + transverse_sign * transverse[ coordinate ]
                )
            for coordinate in range( 3 )
            )
        for lateral_sign, transverse_sign in (
                (1, 1),
                (-1, 1),
                (-1, -1),
                (1, -1),
                )
        ]
    vertices.extend( (start, end) )
    faces = [
        (index, (index + 1) % 4, 5)
        for index in range( 4 )
        ]
    faces.extend(
            (
                (4, 0, 2),
                (4, 1, 3),
                ),
            )
    mesh = Mesh(
            tuple( vertices ),
            tuple( faces ),
            )
    check_mesh( mesh )
    return mesh


def combine_meshes(*meshes: Mesh) -> Mesh:
    """Assemble one or more meshes without unioning or welding surfaces.

    The result retains component boundaries and any geometric overlaps.
    Open input surfaces remain open. Empty input raises ValueError.
    """
    if not meshes:
        raise ValueError( 'We need at least one mesh to combine.' )

    vertices = []
    faces = []
    for mesh in meshes:
        check_mesh( mesh )
        offset = len( vertices )
        vertices.extend( mesh.vertices )
        faces.extend(
                tuple( offset + index for index in face )
                for face in mesh.faces
                )

    return Mesh( tuple( vertices ), tuple( faces ) )
