#!/usr/bin/env python

"""

Classes representing parameters for GeoClaw runs

:Classes:

 - GeoClawData
 - RefinementData
 - TopographyData
 - FixedGridData
 - FGmaxData
 - DTopoData
 - QinitData

:Constants:

 - Rearth - Radius of earth in meters
 - DEG2RAD factor to convert degrees to radians
 - RAD2DEG factor to convert radians to degrees
 - LAT2METER factor to convert degrees in latitude to meters
"""

from __future__ import absolute_import
from __future__ import print_function
import os
import numpy
import clawpack.clawutil.data
import warnings

# Radius of earth in meters.
# For consistency, should always use this value when needed, e.g.
# in setrun.py or topotools:
Rearth = 6367.5e3  # average of polar and equatorial radii

DEG2RAD = numpy.pi / 180.0
RAD2DEG = 180.0 / numpy.pi
LAT2METER = Rearth * DEG2RAD

class GeoClawData(clawpack.clawutil.data.ClawData):
    r"""
    Object containing the basic .

    Note that this data object will write out multiple files.
    """
    def __init__(self):
        super(GeoClawData,self).__init__()

        # GeoClaw physics parameters
        self.add_attribute('gravity',9.8)
        self.add_attribute('rho', 1025.0)  # Density of water kg/m^3
        self.add_attribute('rho_air',1.15) # Density of air kg/m^3
        self.add_attribute('nu', 1.004e-6)  # Kinematic viscosity of water/working fluid
        self.add_attribute('ambient_pressure', 101.3e3) # Nominal atmos pressure
        self.add_attribute('earth_radius',Rearth)
        self.add_attribute('coordinate_system',1)
        self.add_attribute('coriolis_forcing',True)
        self.add_attribute('theta_0',45.0)
        self.add_attribute('friction_forcing',True)
        self.add_attribute('manning_coefficient',[0.025])
        self.add_attribute('manning_break',[])

        # GeoClaw algorithm parameters
        self.add_attribute('dry_tolerance',1e-3)
        self.add_attribute('friction_depth',1.0e6)
        self.add_attribute('sea_level',0.0)


    def write(self,data_source='setrun.py', out_file='geoclaw.data'):

        self.open_data_file(out_file, data_source)

        self.data_write('gravity',
                               description="(gravitational acceleration m/s^2)")
        self.data_write('rho', description="(Density of water kg/m^3)")
        self.data_write('rho_air',description="(Density of air kg/m^3)")
        self.data_write('nu', description="(Kinematic viscosity of water/working fluid m^2/s)")
        self.data_write('ambient_pressure',
                                description="(Nominal atmospheric pressure Pa)")
        self.data_write('earth_radius', description="(Radius of the earth m)")
        self.data_write('coordinate_system')
        self.data_write('sea_level')
        self.data_write()

        # Forcing terms
        self.data_write('coriolis_forcing')
        if self.coordinate_system == 1 and self.coriolis_forcing:
            self.data_write('theta_0')
        self.data_write('friction_forcing')
        if self.friction_forcing:
            if type(self.manning_coefficient) in [int,float]:
                self.manning_coefficient = [self.manning_coefficient]
            num_manning = len(self.manning_coefficient)
            if len(self.manning_break) != num_manning - 1:
                raise IOError("***manning_break array has wrong length")
            self.data_write(value=num_manning,alt_name='num_manning')
            self.data_write('manning_coefficient')
            self.data_write('manning_break')
            self.data_write('friction_depth')

        self.data_write()

        self.data_write('dry_tolerance')

        self.close_data_file()



class RefinementData(clawpack.clawutil.data.ClawData):

    def __init__(self):

        super(RefinementData,self).__init__()

        # Refinement controls
        self.add_attribute('wave_tolerance',1.0e-1)
        self.add_attribute('speed_tolerance',[1.0e12]*6)
        self.add_attribute('deep_depth',None)      # deprecated
        self.add_attribute('max_level_deep',None)  # deprecated
        self.add_attribute('variable_dt_refinement_ratios',False)


    def write(self,data_source='setrun.py', out_file='refinement.data'):
        # Refinement controls
        self.open_data_file(out_file, data_source)
        self.data_write('wave_tolerance')

        # check if user set deprecated parameters:
        if self.deep_depth is not None:
            w = '\n  *** WARNING: deep_depth parameter ignored as of v5.8.0'
            warnings.warn(w, UserWarning)
        if self.max_level_deep is not None:
            w = '\n  *** WARNING: max_level_deep parameter ignored as of v5.8.0'
            warnings.warn(w, UserWarning)

        if not isinstance(self.speed_tolerance,list):
            self.speed_tolerance = [self.speed_tolerance]
        self.data_write('speed_tolerance')
        self.data_write()
        self.data_write('variable_dt_refinement_ratios',
                        description="(Set dt refinement ratios automatically)")
        self.close_data_file()



class TopographyData(clawpack.clawutil.data.ClawData):

    def __init__(self):

        super(TopographyData,self).__init__()

        # Topography data
        self.add_attribute('topo_missing',99999.)
        self.add_attribute('test_topography',0)
        self.add_attribute('topofiles',[])

        # Jump discontinuity
        self.add_attribute('topo_location',-50e3)
        self.add_attribute('topo_left',-4000.0)
        self.add_attribute('topo_right',-200.0)
        self.add_attribute('topo_angle',0.0)

        # Simple oceanic shelf
        self.add_attribute('x0',350e3)
        self.add_attribute('x1',450e3)
        self.add_attribute('x2',480e3)
        self.add_attribute('basin_depth',-3000.0)
        self.add_attribute('shelf_depth',-100.0)
        self.add_attribute('beach_slope',0.008)


    def write(self,data_source='setrun.py', out_file='topo.data'):

        self.open_data_file(out_file, data_source)
        self.data_write(name='topo_missing',
                        description='replace no_data_value in topofile')
        self.data_write(name='test_topography',description='(Type topography specification)')
        if self.test_topography == 0:
            ntopofiles = len(self.topofiles)
            self.data_write(value=ntopofiles,alt_name='ntopofiles')
            for tfile in self.topofiles:

                if len(tfile) == 6:
                    w = '\n  *** WARNING: topofile specs changed in v5.8.0 -- ' + \
                          'Flag level info now ignored'
                    warnings.warn(w, UserWarning)
                    tfile = [tfile[0], tfile[-1]] # drop minlevel,maxlevel,t1,t2
                elif len(tfile) == 2:
                    pass  # now expect only topo_type, filename
                else:
                    raise ValueError('Unexpected len(tfile) = %i' % len(tfile))

                # if path is relative in setrun, assume it's relative to the
                # same directory that out_file comes from
                fname = os.path.abspath(os.path.join(os.path.dirname(out_file),tfile[-1]))
                self._out_file.write("\n'%s' \n " % fname)
                self._out_file.write("%3i   # topo_type\n" % tfile[0])
        elif self.test_topography == 1:
            self.data_write(name='topo_location',description='(Bathymetry jump location)')
            self.data_write(name='topo_left',description='(Depth to left of bathy_location)')
            self.data_write(name='topo_right',description='(Depth to right of bathy_location)')
        elif self.test_topography == 2 or self.test_topography == 3:
            self.data_write(name='x0',description='(Location of basin end)')
            self.data_write(name='x1',description='(Location of shelf slope end)')
            self.data_write(name='x2',description='(Location of beach slope)')
            self.data_write(name='basin_depth',description='(Depth of basin)')
            self.data_write(name='shelf_depth',description='(Depth of shelf)')
            self.data_write(name='beach_slope',description='(Slope of beach)')
        else:
            raise NotImplementedError("Test topography type %s has not been"
                                        " implemented." % self.test_topography)

        self.close_data_file()



class FixedGridData(clawpack.clawutil.data.ClawData):

    def __init__(self):

        super(FixedGridData,self).__init__()

        # Fixed Grids
        self.add_attribute('fixedgrids',[])


    def write(self,data_source='setrun.py', out_file='fixed_grids.data'):
        # Fixed grid settings
        self.open_data_file(out_file, data_source)
        nfixedgrids = len(self.fixedgrids)
        self.data_write(value=nfixedgrids,alt_name='nfixedgrids')
        self.data_write()
        for fixedgrid in self.fixedgrids:
            self._out_file.write(11*"%g  " % tuple(fixedgrid) +"\n")
        self.close_data_file()

class FGmaxData(clawpack.clawutil.data.ClawData):

    def __init__(self):

        super(FGmaxData,self).__init__()

        # File name for fgmax points and parameters:
        self.add_attribute('fgmax_files',[])
        self.add_attribute('num_fgmax_val',1)
        self.add_attribute('fgmax_grids',[])


    def write(self,data_source='setrun.py', out_file='fgmax_grids.data'):
        if len(self.fgmax_files) > 0:
            msg = '*** fgmax_files has been deprecated, ' \
                  + 'use fgmax_grids instead.'
            raise ValueError(msg)

        # new style:
        self.open_data_file(out_file, data_source)
        num_fgmax_val = self.num_fgmax_val
        if num_fgmax_val not in [1,2,5]:
            raise NotImplementedError( \
                    "Expecting num_fgmax_val in [1,2,5], got %s" % num_fgmax_val)
        self.data_write(value=num_fgmax_val,alt_name='num_fgmax_val')
        num_fgmax_grids = len(self.fgmax_grids)
        self.data_write(value=num_fgmax_grids,alt_name='num_fgmax_grids')
        self.data_write()

        fgno_unset = 0  # to use if fg.fgno not set by user
        fgno_list = []  # to check for uniqueness of fgno's

        for fg in self.fgmax_grids:
            # if path is relative in setrun, assume it's relative to the
            # same directory that out_file comes from
            if fg.xy_fname is not None:
                fg.xy_fname = os.path.abspath(os.path.join(\
                              os.path.dirname(out_file),fg.xy_fname))

            if fg.fgno is None:
                # not set by user in setrun
                fgno_unset += 1
                fg.fgno = fgno_unset

            if fg.fgno in fgno_list:
                msg = 'Trying to set fgmax grid number to fgno = %i' % fg.fgno \
                      + '\n             but this fgno was already used' \
                      + '\n             Set unique fgno for each fgmax grid'
                raise ValueError(msg)

            fgno_list.append(fg.fgno)
            fg.write_to_fgmax_data(self._out_file)
        self.close_data_file()



class DTopoData(clawpack.clawutil.data.ClawData):

    def __init__(self):

        super(DTopoData,self).__init__()

        # Moving topograhpy
        self.add_attribute('dtopofiles',[])
        self.add_attribute('dt_max_dtopo', 1.e99)

    def write(self,data_source='setrun.py', out_file='dtopo.data'):

        # Moving topography settings
        self.open_data_file(out_file, data_source)
        mdtopofiles = len(self.dtopofiles)
        self.data_write(value=mdtopofiles,alt_name='mdtopofiles')
        self.data_write()
        for tfile in self.dtopofiles:

            if len(tfile) == 4:
                w = '\n  *** WARNING: dtopofile specs changed in v5.8.0 -- ' + \
                      'Flag level info now ignored'
                warnings.warn(w, UserWarning)
                tfile = [tfile[0], tfile[-1]]  # drop minlevel,maxlevel
            elif len(tfile) == 2:
                pass   # now expect only dtopo_type, filename
            else:
                raise ValueError('Unexpected len(tfile) = %i' % len(tfile))

            # if path is relative in setrun, assume it's relative to the
            # same directory that out_file comes from
            fname = os.path.abspath(os.path.join(os.path.dirname(out_file),tfile[-1]))
            self._out_file.write("\n'%s' \n" % fname)
            self._out_file.write("%3i   # dtopo_type\n" % tfile[0])
        self.data_write()
        self.data_write(value=self.dt_max_dtopo,alt_name='dt_max_dtopo')
        self.close_data_file()


    def read(self, path, force=False):
        r"""Read a dtopography data file."""

        print(self.dtopofiles)

        with open(os.path.abspath(path), 'r') as data_file:

            file_name = None

            # Forward to first parameter
            for line in data_file:

                # Regular parameter setting
                if "=:" in line:
                    value, tail = line.split("=:")
                    varname = tail.split()[0]

                    if varname == "mdtopofiles":
                        num_dtopo_files = int(value)
                    elif varname == "dt_max_dtopo":
                        self.dt_max_dtopo = float(value)

                # Assume this is the second line of a record, complete and add
                # to dtopofiles list
                elif file_name is not None:
                    base_values = [int(value) for value in line.split()]
                    base_values.append(file_name)
                    self.dtopofiles.append(base_values)
                    file_name = None

                # Non-empty line, assume start of dtopo_file record
                elif line[0] == "'":
                    file_name = line.strip()[1:-1]

        # Check to make sure we have all the dtopofiles
        if len(self.dtopofiles) != num_dtopo_files:
            raise IOError("The number of dtopo files specified does not equal ",
                          "the number found.")



class ForceDry(clawpack.clawutil.data.ClawData):

    def __init__(self):
        r"""
        A single force_dry array and associated data
        """

        super(ForceDry,self).__init__()
        self.add_attribute('tend',None)
        self.add_attribute('fname','')


class QinitData(clawpack.clawutil.data.ClawData):

    def __init__(self):

        super(QinitData,self).__init__()

        # Qinit data
        self.add_attribute('qinit_type',0)
        self.add_attribute('qinitfiles',[])
        self.add_attribute('variable_eta_init',False)
        self.add_attribute('force_dry_list',[])
        self.add_attribute('num_force_dry',0)

    def write(self,data_source='setrun.py', out_file='qinit.data'):

        # Initial perturbation
        self.open_data_file(out_file, data_source)
        self.data_write('qinit_type')

        # Perturbation requested
        if self.qinit_type == 0:
            pass
        else:
            # Check to see if each qinit file is present and then write the data
            for tfile in self.qinitfiles:

                if len(tfile) == 3:
                    w = '\n  *** WARNING: qinit specs changed in v5.8.0 -- ' + \
                          'Flag level info now ignored'
                    warnings.warn(w, UserWarning)
                    tfile = [tfile[-1]]  # drop minlevel,maxlevel
                elif len(tfile) == 1:
                    pass  # now expect only filename
                else:
                    raise ValueError('Unexpected len(tfile) = %i' % len(tfile))

                # if path is relative in setrun, assume it's relative to the
                # same directory that out_file comes from
                fname = os.path.abspath(os.path.join(os.path.dirname(out_file),tfile[-1]))
                self._out_file.write("\n'%s' \n" % fname)
        # else:
        #     raise ValueError("Invalid qinit_type parameter %s." % self.qinit_type)


        self.data_write('variable_eta_init')

        self.num_force_dry = len(self.force_dry_list)
        self.data_write('num_force_dry')

        for force_dry in self.force_dry_list:

            # if path is relative in setrun, assume it's relative to the
            # same directory that out_file comes from
            fname = os.path.abspath(os.path.join(os.path.dirname(out_file),\
                    force_dry.fname))
            self._out_file.write("\n'%s' \n" % fname)
            self._out_file.write("%.3f \n" % force_dry.tend)


        self.close_data_file()


# Storm data
class SurgeData(clawpack.clawutil.data.ClawData):
    r"""Data object describing storm surge related parameters"""

    # Provide some mapping between model names and integers
    storm_spec_dict_mapping = {"HWRF":-1,
                               None: 0,
                               'holland80': 1,
                               'holland10': 2,
                               'CLE': 3,
                               'SLOSH': 4,
                               'rankine': 5,
                               'modified-rankine': 6,
                               'DeMaria': 7
                              }
    storm_spec_not_implemented = ['CLE']

    def __init__(self):
        super(SurgeData,self).__init__()

        # Source term controls
        self.add_attribute('wind_forcing',False)
        self.add_attribute('drag_law',1)
        self.add_attribute('pressure_forcing',False)

        # Algorithm parameters - Indexing is python based
        self.add_attribute("wind_index", 4)
        self.add_attribute("pressure_index", 6)
        self.add_attribute("display_landfall_time", False)

        # AMR parameters
        self.add_attribute('wind_refine',[20.0,40.0,60.0])
        self.add_attribute('R_refine',[60.0e3,40e3,20e3])

        # Storm parameters
        self.add_attribute('storm_type', None)  # Backwards compatibility
        self.add_attribute('storm_specification_type', 0) # Type of parameterized storm
        self.add_attribute("storm_file", None) # File(s) containing data


    def write(self,out_file='surge.data',data_source="setrun.py"):
        """Write out the data file to the path given"""

        # print "Creating data file %s" % out_file
        self.open_data_file(out_file,data_source)

        self.data_write('wind_forcing', description='(Wind source term used)')
        self.data_write('drag_law', description='(Type of drag law to use)')
        self.data_write('pressure_forcing',
                        description="(Pressure source term used)")
        self.data_write()

        self.data_write("wind_index", value=self.wind_index + 1,
                        description="(Index into aux array - fortran indexing)")
        self.data_write("pressure_index", value=self.pressure_index +  1,
                        description="(Index into aux array - fortran indexing)")
        self.data_write("display_landfall_time",
                        description='(Display time relative to landfall)')
        self.data_write()

        if isinstance(self.wind_refine, bool):
            if not self.wind_refine:
                self.data_write('wind_refine', value=False,
                                description='(Refinement ratios)')
        elif isinstance(self.wind_refine, type(None)):
            self.data_write('wind_refine', value=False,
                            description='(Refinement ratios)')
        else:
            self.data_write('wind_refine',description='(Refinement ratios)')
        if isinstance(self.R_refine, bool):
            if not self.R_refine:
                self.data_write('R_refine', value=False,
                                description='(Refinement ratios)')
        elif isinstance(self.R_refine, type(None)):
            self.data_write('R_refine', value=False,
                            description='(Refinement ratios)')
        else:
            self.data_write('R_refine', description='(Refinement ratios)')
        self.data_write()

        # Storm specification
        if self.storm_type is not None:
            self.storm_specification_type = self.storm_type
        if type(self.storm_specification_type) is not int:
            if self.storm_specification_type in         \
                    self.storm_spec_dict_mapping.keys():
                if self.storm_specification_type in     \
                    self.storm_spec_not_implemented:
                    raise NotImplementedError("%s has not been implemented."
                                %self.storm_specification_type)

                else:
                    self.data_write("storm_specification_type",
                                self.storm_spec_dict_mapping[
                                        self.storm_specification_type],
                                description="(Storm specification)")
            else:
                raise ValueError("Unknown storm specification type %s"
                                 % self.storm_specification_type)
        else:
            self.data_write("storm_specification_type",
                            description="(Storm specification)")
        self.data_write("storm_file", description='(Path to storm data)')

        self.close_data_file()


class FrictionData(clawpack.clawutil.data.ClawData):
    r"""Data class representing complex variable friction"""

    def __init__(self):
        r""""""

        super(FrictionData, self).__init__()

        # Variable friction support
        self.add_attribute('variable_friction', False)

        # Index where the variable friction field is stored (Python indexed)
        self.add_attribute('friction_index', 3)

        # Region support
        self.add_attribute('friction_regions', [])

        # File support
        self.add_attribute('friction_files', [])

    def write(self, out_file='friction.data', data_source='setrun.py'):

        self.open_data_file(out_file, data_source)

        self.data_write('variable_friction',
                        description="(method for setting variable friction)")
        self.data_write('friction_index', value=self.friction_index + 1,
                        description=("(Index into aux array ",
                                     "- fortran indexing)"))
        self.data_write()
        if self.variable_friction:
            # Region based friction
            self.data_write(value=len(self.friction_regions),
                            alt_name='num_friction_regions',
                            description="(Friction Regions)")
            self.data_write()
            for region in self.friction_regions:
                self.data_write(value=region[0], alt_name="lower")
                self.data_write(value=region[1], alt_name="upper")
                self.data_write(value=region[2], alt_name="depths")
                self.data_write(value=region[3],
                                alt_name="manning_coefficients")
                self.data_write()

            # File based friction
            self.data_write(value=len(self.friction_files),
                            alt_name='num_friction_files')
            for friction_file in self.friction_files:
                # if path is relative in setrun, assume it's relative to the
                # same directory that out_file comes from
                fname = os.path.abspath(os.path.join(os.path.dirname(out_file),friction_file))
                self._out_file.write("'%s' %s\n " % fname)

        self.close_data_file()


class MultilayerData(clawpack.clawutil.data.ClawData):
    r"""
    Multilayer SWE data object
    """

    def __init__(self):
        super(MultilayerData, self).__init__()

        # Physics parameters
        self.add_attribute('num_layers', 1)
        self.add_attribute('rho', [1025.0, 1028.0])
        self.add_attribute('eta', [0.0, -200.0])
        self.add_attribute('wave_tolerance', [1.e-1, 1.e-1])

        # Algorithm parameters
        self.add_attribute('eigen_method', 4)
        self.add_attribute('inundation_method', 2)
        self.add_attribute('check_richardson', True)
        self.add_attribute('richardson_tolerance', 0.95)
        self.add_attribute('layer_index', 8)

        # Need to adjust refinement module for this, dry_limit is in geodata
        self.add_attribute('wave_tolerance', [1e-1, 2e-1])
        self.add_attribute('dry_limit', False)

    def write(self, out_file='multilayer.data', datasource="setrun.py"):

        self.open_data_file(out_file, datasource)

        self.data_write('num_layers', description='(Number of layers)')
        self.data_write('eta',
                        description='(Initial top surface of each layer)')
        self.data_write('wave_tolerance',
                        description=('(Tolerance of surface perturbation per',
                                     ' layer, used for refinement criteria)'))
        self.data_write('layer_index', value=self.layer_index + 1,
                        description=("(Index into aux array -",
                                     " fortran indexing)"))
        self.data_write(None)
        self.data_write('check_richardson',
                        description="(Check Richardson number)")
        self.data_write('richardson_tolerance',
                        description='(Tolerance for Richardson number)')
        self.data_write('eigen_method',
                        description='(Method for calculating eigenspace)')
        self.data_write('inundation_method',
                        description=('(Method for calculating inundation ',
                                     'eigenspace)'))
        self.close_data_file()


# Point source data
class PointSourceData(clawpack.clawutil.data.ClawData):
    """Data object describing point sources"""

    def __init__(self):
        """Constructor of PointSourceData class"""

        super(PointSourceData, self).__init__()

        # number of point sources
        self.add_attribute('n_point_sources', 0)

        # a list of point sources
        self.add_attribute('point_sources', [])

    def write(self, out_file='./point_source.data', data_source="setrun.py"):
        """Write out the data file to the path given"""

        # check data consistency
        self._check()

        # open the output file
        self.open_data_file(out_file, data_source)

        # write number of point sources
        self.data_write('n_point_sources', description='Number of point sources')

        # write point sources
        for i, pts in enumerate(self.point_sources):
            self.data_write() # a blank line
            self.data_write("id", i, description="ID of this point source")
            self.data_write("coord", pts[0], description="coordinates")
            self.data_write("n_times", pts[1], description="number of time segments")
            self.data_write("end_times", pts[2], description="end times of segments")
            self.data_write("vol_rates", pts[3], description="volumetric rates of segments")

        # close the output file
        self.close_data_file()

    def _check(self):
        """Check if the data are consistent"""

        # check if the number of data set match n_point_sources
        assert self.n_point_sources == len(self.point_sources),  \
            "The number of point sources is not consistent with point source data."

        # check the records of point sources
        for i, pts in enumerate(self.point_sources):
            assert len(pts) == 4, "There should be 4 records in the data of " \
                "the {}-th point source.".format(i)
            assert isinstance(pts[0], list), "The coordinate of the {}-th " \
                "point source is not a Python list.".format(i)
            assert len(pts[0]) == 2, "The coordinate of the {}-th point " \
                "is not in the format of [x, y].".format(i)
            assert isinstance(pts[1], int), "The 2nd record in the data of " \
                "the {}-th point source should be an integer for the number " \
                "of time segments.".format(i)
            assert isinstance(pts[2], list), "The end times of the time segments " \
                "of the {}-th point source is not a Python list.".format(i)
            assert len(pts[2]) == pts[1], "The number of end times does not " \
                "match the integer provided for the {}-th point source.".format(i)
            assert sorted(pts[2]) == pts[2], "The list of end times is not " \
                "sorted in an ascending order."
            assert isinstance(pts[3], list), "The volumetric rates of the time " \
                "segments of the {}-th point source is not a Python list.".format(i)
            assert len(pts[3]) == pts[1], "The number of volumetric rates does " \
                "not match the integer provided for the {}-th point source.".format(i)


# Darcy-Weisbach data
class DarcyWeisbachData(clawpack.clawutil.data.ClawData):
    """Data object describing Darcy-Weisbach friction model"""

    def __init__(self):
        """Constructor of DarcyWeisbachData class"""

        super(DarcyWeisbachData, self).__init__()

        # type of the friction coefficients
        # 0: trun off the feature and return control to GeoClaw's Manning friction
        # 1: constant coefficient everywhere
        # 2: block-wise constants
        # 3: cell-wise coefficients
        # 4: three-regime coefficient model
        # 5: Churchill's coefficient model
        # 6: two-regime coefficient model: laminar + Colebrook-White
        self.add_attribute('type', 0)

        # friction_tol, the same as friction_tol in GeoClaw.
        # TODO: merge the friction models of GeoClaw and landspill
        self.add_attribute('friction_tol', 1e6)

        # dry_tol, the same as dry_tolerance in GeoClaw.
        # TODO: merge dry_tol and dry_tolerance from GeoClaw and landspill
        self.add_attribute('dry_tol', 1e-6)

        # single constant coefficient.
        self.add_attribute('coefficient', 0.25)

        # default coefficient; only meaningful for type 2 and 3
        self.add_attribute('default_coefficient', 0.25)

        # number of blocks; only meaningful for type 2
        self.add_attribute('n_blocks', 0)

        # blocks' corners; only meaningful for type 2
        self.add_attribute('xlowers', [])
        self.add_attribute('xuppers', [])
        self.add_attribute('ylowers', [])
        self.add_attribute('yuppers', [])

        # coefficients; only meaningful for type 2
        self.add_attribute('coefficients', [])

        # filename; only meaningful for type 3, 4, 5, 6
        self.add_attribute('filename', '')

        # default_roughness; only meaningful for type 4, 5, 6
        self.add_attribute('default_roughness', 0.0)

    def write(self, out_file='./darcy_weisbach.data', data_source="setrun.py"):
        """Write out the data file to the path given"""

        # check data consistency
        self._check()

        # open the output file
        self.open_data_file(out_file, data_source)

        # write number of point sources
        self.data_write('type', description='Type of Darcy-Weisbach coefficient')

        # if this deature is disabled, close the file and return
        if self.type == 0:
            self.close_data_file()
            return

        # for other non-zero options
        self.data_write('friction_tol', description='Same meanining as the ' +
                        'friction_depth in original GeoClaw setting.')
        self.data_write('dry_tol', description='Same meaning as the ' +
                        'dry_tolerance in original GeoClaw setting.')

        if self.type == 1:
            self.data_write('coefficient',
                            description="Darcy-Weisbach coefficient")
        elif self.type == 2:
            self.data_write('default_coefficient',
                            description="coefficient for uncovered areas")
            self.data_write('n_blocks',
                            description="number of blocks")
            self.data_write('xlowers',
                            description="x lower coords for blocks")
            self.data_write('xuppers',
                            description="x upper coords for blocks")
            self.data_write('ylowers',
                            description="x lower coords for blocks")
            self.data_write('yuppers',
                            description="x upper coords for blocks")
            self.data_write('coefficients',
                            description="coefficients in blocks")
        elif self.type == 3:
            self.filename = os.path.abspath(self.filename)
            self.data_write('filename',
                            description="Escri ASCII file for coefficients")
            self.data_write('default_coefficient',
                            description="coefficient for cells not covered by the file")
        elif self.type in [4, 5, 6]:
            self.filename = os.path.abspath(self.filename)
            self.data_write('filename',
                            description="Escri ASCII file for roughness")
            self.data_write('default_roughness',
                            description="roughness for cells not covered by the file")

        # close the output file
        self.close_data_file()

    def _check(self):
        """Check if the data are consistent"""

        assert isinstance(self.type, int), "Type should be an integer."

        # 0: this feature disabled
        if self.type == 0:
            return

        # common data for non-zero options
        assert isinstance(self.friction_tol, float), \
            "friction_tol shoudl be a floating number."
        assert isinstance(self.dry_tol, float), \
            "dry_toll shoudl be a floating number."

        # non-zero options
        if self.type == 1:
            assert isinstance(self.default_coefficient, float), \
                "default_coefficient shoudl be a floating number."
        elif self.type == 2:
            assert isinstance(self.n_blocks, int), \
                "n_blocks shoudl be a floating number."
            assert isinstance(self.xlowers, list), \
                "xlowers shoudl be a list."
            assert len(self.xlowers) == self.n_blocks, \
                "the length of xlowers shoudl be n_blocks."
            assert isinstance(self.xuppers, list), \
                "xuppers shoudl be a list."
            assert len(self.xuppers) == self.n_blocks, \
                "the length of xuppers shoudl be n_blocks."
            assert isinstance(self.ylowers, list), \
                "ylowers shoudl be a list."
            assert len(self.ylowers) == self.n_blocks, \
                "the length of ylowers shoudl be n_blocks."
            assert isinstance(self.yuppers, list), \
                "yuppers shoudl be a list."
            assert len(self.yuppers) == self.n_blocks, \
                "the length of yuppers shoudl be n_blocks."
            assert isinstance(self.coefficients, list), \
                "coefficients shoudl be a list."
            assert len(self.coefficients) == self.n_blocks, \
                "the length of coefficients shoudl be n_blocks."
        elif self.type in [3, 4, 5, 6]:
            assert isinstance(self.filename, str), \
                "filename should be a string."
            assert self.filename != "", \
                "filename can not be empty."

            if self.type == 3:
                assert isinstance(self.default_coefficient, float), \
                    "default_coefficient shoudl be a float"
            else:
                assert isinstance(self.default_roughness, float), \
                    "default_roughness shoudl be a float"
        else:
            raise ValueError("Type values outside [0, 5] not allowed.")
