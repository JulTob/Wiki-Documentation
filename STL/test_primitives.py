"""Check geometry against analytic shapes and representative invalid inputs."""

import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert( 0, str( Path( __file__ ).resolve().parents[ 1 ] ) )
from geometry.primitives import (
    arrow_mesh,
    combine_meshes,
    crossed_pyramid_arrow_mesh,
    cube_point_mesh,
    point_mesh,
    sphere_mesh,
    )
from mesh_tools import check_mesh, cross, dot, face_normal, length, subtract, unit


class PrimitiveChecks(unittest.TestCase):
    def test_translated_sphere_has_requested_centre_and_radius(self):
        centre = (3.0, -2.0, 1.0)
        mesh = sphere_mesh(
                2.0,
                12,
                24,
                centre=centre,
                )
        for vertex in mesh.vertices:
            self.assertAlmostEqual( length( subtract( vertex, centre ) ), 2.0 )
        for face in mesh.faces:
            radial = subtract( mesh.vertices[ face[ 0 ] ], centre )
            self.assertGreater( dot( face_normal( mesh, face ), radial ), 0 )

    def test_smoother_default_is_closed_and_approaches_sphere_volume(self):
        mesh = sphere_mesh( 1.0 )
        result = check_mesh( mesh, closed=True )
        exact = 4 * math.pi / 3
        self.assertEqual( len( mesh.faces ), 3968 )
        self.assertEqual( result.vertex_graph_components, 1 )
        self.assertLess( abs( exact - result.signed_volume_if_closed ), 0.02 )

    def test_point_radius_is_a_spatial_marker_around_its_position(self):
        position = (-2.0, 0.5, 3.0)
        mesh = point_mesh( position, 0.125 )
        for vertex in mesh.vertices:
            distance = length( subtract( vertex, position ) )
            self.assertAlmostEqual( distance, 0.125 )
        self.assertEqual(
                check_mesh( mesh, closed=True ).vertex_graph_components,
                1,
                )

    def test_arrow_volume_matches_polygonal_cylinder_and_cone(self):
        sides = 24
        shaft_radius = 0.1
        head_radius = 0.3
        head_length = 0.6
        polygon_factor = sides * math.sin( 2 * math.pi / sides ) / 2
        expected = polygon_factor * (
            shaft_radius**2 * (3 - head_length)
            + head_radius**2 * head_length / 3
            )
        for start, end in (
                ((0, 0, 0), (3, 0, 0)),
                ((1, 2, 3), (1, 2, 0)),
                ((-2, 1, 0.5), (-1, 3, 2.5)),
                ):
            mesh = arrow_mesh(
                    start,
                    end,
                    shaft_radius=shaft_radius,
                    head_radius=head_radius,
                    head_length=head_length,
                    sides=sides,
                    )
            result = check_mesh( mesh, closed=True )
            self.assertEqual( result.vertex_graph_components, 1 )
            self.assertAlmostEqual( result.signed_volume_if_closed, expected )

    def test_arrow_extents_follow_its_endpoints_in_any_direction(self):
        for end in ((0, 0, 2), (0, -2, 0), (1e-12, 2, 1e-12), (1, -2, 3)):
            start = (0, 0, 0)
            mesh = arrow_mesh( start, end )
            distance = length( end )
            axis = unit( end )
            projections = [dot( vertex, axis ) for vertex in mesh.vertices]
            self.assertAlmostEqual( min( projections ), 0 )
            self.assertAlmostEqual( max( projections ), distance )
            self.assertEqual( mesh.vertices[ -2 ], start )
            self.assertEqual( mesh.vertices[ -1 ], end )

    def test_composition_retains_distinct_components(self):
        first = point_mesh( (0, 0, 0), 0.1 )
        second = arrow_mesh( (1, 0, 0), (2, 1, 0) )
        scene = combine_meshes( first, second )
        self.assertEqual(
                check_mesh( scene, closed=True ).vertex_graph_components,
                2,
                )
        self.assertEqual(
                len( scene.faces ),
                len( first.faces ) + len( second.faces ),
                )
        self.assertEqual( scene.vertices[ :len( first.vertices ) ], first.vertices )

    def test_invalid_spheres_and_points_raise_clear_errors(self):
        for radius in (0, -1, math.nan, math.inf):
            with self.assertRaises( ValueError ):
                sphere_mesh( radius )
        for count in (2, 3.5, True):
            with self.assertRaisesRegex( ValueError, 'integer' ):
                sphere_mesh( 1, latitude_steps=count )
        for centre in ((1, 2), (0, math.nan, 0), (0, math.inf, 0)):
            with self.assertRaisesRegex( ValueError, 'coordinates' ):
                point_mesh( centre, 0.1 )

    def test_invalid_arrows_and_empty_composition_are_rejected(self):
        for options in (
                {'shaft_radius': 0},
                {'head_radius': 0.01, 'shaft_radius': 0.1},
                {'head_length': 1},
                {'sides': 2},
                ):
            with self.assertRaises( ValueError ):
                arrow_mesh( (0, 0, 0), (1, 0, 0), **options )
        with self.assertRaisesRegex( ValueError, 'Arrow length' ):
            arrow_mesh( (1, 2, 3), (1, 2, 3) )
        with self.assertRaisesRegex( ValueError, 'at least one' ):
            combine_meshes()


class LowPolyChecks(unittest.TestCase):
    def test_cube_bounds_and_outward_volume_match_analytic_cube(self):
        position = (3.0, -2.0, 1.5)
        side = 0.5
        mesh = cube_point_mesh( position, side )
        checks = check_mesh( mesh, closed=True )
        self.assertEqual( len( mesh.vertices ), 8 )
        self.assertEqual( len( mesh.faces ), 12 )
        self.assertEqual( checks.vertex_graph_components, 1 )
        self.assertAlmostEqual( checks.signed_volume_if_closed, side**3 )
        for coordinate in range( 3 ):
            values = [vertex[ coordinate ] for vertex in mesh.vertices]
            self.assertEqual( min( values ), position[ coordinate ] - side / 2 )
            self.assertEqual( max( values ), position[ coordinate ] + side / 2 )
        for face in mesh.faces:
            outward = subtract( mesh.vertices[ face[ 0 ] ], position )
            self.assertGreater( dot( face_normal( mesh, face ), outward ), 0 )

    def test_cube_projected_area_matches_box_formula(self):
        side = 0.4
        mesh = cube_point_mesh( (0, 0, 0), side )
        for view in ((1, 0, 0), (1, 1, 0), (1, 2, 3)):
            view = unit( view )
            projected_area = 0.0
            for face in mesh.faces:
                first, second, third = (mesh.vertices[ i ] for i in face)
                area_vector = cross(
                        subtract( second, first ),
                        subtract( third, first ),
                        )
                projected_area += abs( dot( area_vector, view ) ) / 4
            self.assertAlmostEqual(
                    projected_area,
                    side**2 * sum( abs( component ) for component in view ),
                    )

    def test_pyramid_square_and_axial_extents_match_explicit_sizes(self):
        width = 0.4
        head_length = 0.7
        for start, end in (
                ((0, 0, 0), (0, 0, 3)),
                ((2, 1, -1), (-1, 1, -1)),
                ((-2, 1, 0.5), (-1, 3, 2.5)),
                ((0, 0, 0), (1e-12, 3, 1e-12)),
                ):
            mesh = crossed_pyramid_arrow_mesh(
                    start,
                    end,
                    head_width=width,
                    head_length=head_length,
                    )
            axis = unit( subtract( end, start ) )
            distance = length( subtract( end, start ) )
            centre = tuple(
                sum( vertex[ coordinate ] for vertex in mesh.vertices[ :4 ] ) / 4
                for coordinate in range( 3 )
                )
            for coordinate in range( 3 ):
                self.assertAlmostEqual(
                        centre[ coordinate ],
                        end[ coordinate ] - head_length * axis[ coordinate ],
                        )
            for index in range( 4 ):
                corner = mesh.vertices[ index ]
                following = mesh.vertices[ (index + 1) % 4 ]
                radial = subtract( corner, centre )
                self.assertAlmostEqual( length( radial ), width / math.sqrt( 2 ) )
                self.assertAlmostEqual(
                        length( subtract( corner, following ) ),
                        width,
                        )
                self.assertAlmostEqual( dot( radial, axis ), 0 )
            for face in mesh.faces[ :4 ]:
                radial = subtract( mesh.vertices[ face[ 0 ] ], centre )
                self.assertGreater( dot( face_normal( mesh, face ), radial ), 0 )
            projections = [
                dot( subtract( vertex, start ), axis )
                for vertex in mesh.vertices
                ]
            self.assertAlmostEqual( min( projections ), 0 )
            self.assertAlmostEqual( max( projections ), distance )
            self.assertEqual( mesh.vertices[ -2 ], start )
            self.assertEqual( mesh.vertices[ -1 ], end )

    def test_pyramid_layout_has_six_open_crossing_faces(self):
        mesh = crossed_pyramid_arrow_mesh( (0, 0, 0), (2, 1, 1) )
        checks = check_mesh( mesh )
        self.assertEqual( len( mesh.vertices ), 6 )
        self.assertEqual( len( mesh.faces ), 6 )
        self.assertEqual( mesh.faces[ -2: ], ((4, 0, 2), (4, 1, 3)) )
        self.assertEqual( checks.boundary_edges, 10 )
        self.assertEqual( checks.vertex_graph_components, 1 )
        self.assertIsNone( checks.signed_volume_if_closed )
        with self.assertRaisesRegex( ValueError, 'boundary' ):
            check_mesh( mesh, closed=True )

    def test_crossed_fins_have_side_coverage_and_vanish_end_on(self):
        width = 0.4
        head_length = 0.7
        start = (1, -2, 3)
        end = (2, 0, 6)
        axis = unit( subtract( end, start ) )
        distance = length( subtract( end, start ) )
        mesh = crossed_pyramid_arrow_mesh(
                start,
                end,
                head_width=width,
                head_length=head_length,
                )
        normals = [face_normal( mesh, face ) for face in mesh.faces[ -2: ]]
        expected_area = width * math.sqrt( 2 ) * (distance - head_length) / 2
        self.assertAlmostEqual( dot( normals[ 0 ], normals[ 1 ] ), 0 )
        for face in mesh.faces[ -2: ]:
            first, second, third = (mesh.vertices[ i ] for i in face)
            area_vector = cross(
                    subtract( second, first ),
                    subtract( third, first ),
                    )
            self.assertAlmostEqual( length( area_vector ) / 2, expected_area )
            self.assertAlmostEqual( dot( area_vector, axis ), 0 )
        for angle in (0, math.pi / 8, math.pi / 4, math.pi / 2):
            view = tuple(
                math.cos( angle ) * normals[ 0 ][ coordinate ]
                + math.sin( angle ) * normals[ 1 ][ coordinate ]
                for coordinate in range( 3 )
                )
            total_area = expected_area * sum(
                    abs( dot( normal, view ) )
                    for normal in normals
                    )
            self.assertGreaterEqual( total_area, expected_area * (1 - 1e-12) )

    def test_default_sizes_and_world_frame_are_deterministic(self):
        for end in ((1, 1, 1), (1 - 1e-9, 1, 1), (1 + 1e-9, 1, 1)):
            distance = length( end )
            mesh = crossed_pyramid_arrow_mesh( (0, 0, 0), end )
            self.assertEqual(
                    mesh,
                    crossed_pyramid_arrow_mesh(
                            (0, 0, 0),
                            end,
                            head_width=0.12 * distance,
                            head_length=0.22 * distance,
                            ),
                    )
            checks = check_mesh( mesh )
            self.assertEqual( checks.boundary_edges, 10 )
            self.assertEqual(
                    mesh,
                    crossed_pyramid_arrow_mesh( (0, 0, 0), end ),
                    )
        tied = crossed_pyramid_arrow_mesh( (0, 0, 0), (1, 1, 1) )
        actual_lateral = unit( subtract( tied.vertices[ 0 ], tied.vertices[ 1 ] ) )
        first_axis_lateral = unit( cross( unit( (1, 1, 1) ), (1, 0, 0) ) )
        for actual, expected in zip( actual_lateral, first_axis_lateral ):
            self.assertAlmostEqual( actual, expected )

    def test_new_helpers_reject_invalid_sizes_and_coordinates(self):
        for size in (0, -1, math.nan, math.inf, 10**1000):
            with self.assertRaisesRegex( ValueError, 'Marker size' ):
                cube_point_mesh( (0, 0, 0), size )
            with self.assertRaisesRegex( ValueError, 'Head width' ):
                crossed_pyramid_arrow_mesh(
                        (0, 0, 0),
                        (1, 0, 0),
                        head_width=size,
                        )
            with self.assertRaisesRegex( ValueError, 'Head length' ):
                crossed_pyramid_arrow_mesh(
                        (0, 0, 0),
                        (1, 0, 0),
                        head_length=size,
                        )
        for position in ((1, 2), (0, math.nan, 0), (0, 0, math.inf)):
            with self.assertRaisesRegex( ValueError, 'coordinates' ):
                cube_point_mesh( position, 0.1 )
            for start, end in ((position, (0, 0, 0)), ((0, 0, 0), position)):
                with self.assertRaisesRegex( ValueError, 'coordinates' ):
                    crossed_pyramid_arrow_mesh( start, end )

    def test_arrow_rejects_zero_overflowed_and_excess_head_lengths(self):
        for start, end in (
                ((1, 2, 3), (1, 2, 3)),
                ((-1e308, 0, 0), (1e308, 0, 0)),
                ):
            with self.assertRaisesRegex( ValueError, 'Arrow length' ):
                crossed_pyramid_arrow_mesh( start, end )
        for head_length in (1, 2):
            with self.assertRaisesRegex( ValueError, 'shorter' ):
                crossed_pyramid_arrow_mesh(
                        (0, 0, 0),
                        (1, 0, 0),
                        head_length=head_length,
                        )

    def test_unrepresentable_translated_shapes_fail_instead_of_flattening(self):
        with self.assertRaisesRegex( ValueError, 'unresolved' ):
            cube_point_mesh( (1e16, 1e16, 1e16), 1e-6 )
        with self.assertRaisesRegex( ValueError, 'unresolved' ):
            crossed_pyramid_arrow_mesh(
                    (1e16, 1e16, 1e16),
                    (1e16 + 4, 1e16, 1e16),
                    head_width=1e-6,
                    )
        with self.assertRaisesRegex( ValueError, 'unresolved' ):
            crossed_pyramid_arrow_mesh(
                    (1e16, 0, 0),
                    (1e16 + 4, 0, 0),
                    head_length=1e-30,
                    )

    def test_export_script_runs_elsewhere_and_checks_parsed_stl(self):
        script = Path( __file__ ).with_name( 'make_low_poly_scene.py' ).resolve()
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path( temporary ) / 'generated'
            subprocess.run(
                    [
                        sys.executable,
                        '-B',
                        str( script ),
                        '--output',
                        str( destination ),
                        ],
                    cwd=temporary,
                    check=True,
                    capture_output=True,
                    text=True,
                    )
            scene = json.loads( (destination / 'scene.json').read_text() )
            checks = json.loads( (destination / 'checks.json').read_text() )
            self.assertEqual( len( scene[ 'components' ] ), 2 )
            self.assertTrue( scene[ 'rendering' ][ 'two_sided_rendering_required' ] )
            self.assertFalse( scene[ 'rendering' ][ 'destination_viewer_tested' ] )
            self.assertEqual( checks[ 'scene' ][ 'faces' ], 18 )
            self.assertEqual( checks[ 'scene' ][ 'vertex_graph_components' ], 2 )
            for name, count in (
                    ('cube', 12),
                    ('crossed-pyramid-arrow', 6),
                    ('scene', 18),
                    ):
                record = checks[ name ][ 'stl_export' ]
                self.assertEqual( record[ 'parsed_facets' ], count )
                self.assertEqual( record[ 'parsed_vertex_records' ], 3 * count )
                self.assertTrue( record[ 'coordinates_match_source' ] )
                self.assertTrue( record[ 'unit_normals_match_parsed_winding' ] )


if __name__ == '__main__':
    unittest.main()
