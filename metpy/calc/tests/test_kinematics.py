# Copyright (c) 2008-2015 MetPy Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause
"""Test the `kinematics` module."""

import numpy as np

from metpy.calc import (advection, convergence_vorticity, geostrophic_wind, h_convergence,
                        v_vorticity)
from metpy.constants import g, omega, Re
from metpy.testing import assert_almost_equal, assert_array_equal
from metpy.units import concatenate, units


def test_zero_gradient():
    """Test convergence_vorticity when there is no gradient in the field."""
    u = np.ones((3, 3)) * units('m/s')
    c, v = convergence_vorticity(u, u, 1 * units.meter, 1 * units.meter)
    truth = np.zeros_like(u) / units.sec
    assert_array_equal(c, truth)
    assert_array_equal(v, truth)


def test_cv_zero_vorticity():
    """Test convergence_vorticity when there is only convergence."""
    a = np.arange(3)
    u = np.c_[a, a, a] * units('m/s')
    c, v = convergence_vorticity(u, u.T, 1 * units.meter, 1 * units.meter)
    true_c = 2. * np.ones_like(u) / units.sec
    true_v = np.zeros_like(u) / units.sec
    assert_array_equal(c, true_c)
    assert_array_equal(v, true_v)


def test_convergence_vorticity():
    """Test of vorticity and divergence calculation for basic case."""
    a = np.arange(3)
    u = np.c_[a, a, a] * units('m/s')
    c, v = convergence_vorticity(u, u, 1 * units.meter, 1 * units.meter)
    true_c = np.ones_like(u) / units.sec
    true_v = np.ones_like(u) / units.sec
    assert_array_equal(c, true_c)
    assert_array_equal(v, true_v)


def test_zero_vorticity():
    """Test vorticity calculation when zeros should be returned."""
    a = np.arange(3)
    u = np.c_[a, a, a] * units('m/s')
    v = v_vorticity(u, u.T, 1 * units.meter, 1 * units.meter)
    true_v = np.zeros_like(u) / units.sec
    assert_array_equal(v, true_v)


def test_vorticity():
    """Test vorticity for simple case."""
    a = np.arange(3)
    u = np.c_[a, a, a] * units('m/s')
    v = v_vorticity(u, u, 1 * units.meter, 1 * units.meter)
    true_v = np.ones_like(u) / units.sec
    assert_array_equal(v, true_v)


def test_zero_convergence():
    """Test convergence calculation when zeros should be returned."""
    a = np.arange(3)
    u = np.c_[a, a, a] * units('m/s')
    c = h_convergence(u, u.T, 1 * units.meter, 1 * units.meter)
    true_c = 2. * np.ones_like(u) / units.sec
    assert_array_equal(c, true_c)


def test_convergence():
    """Test convergence for simple case."""
    a = np.arange(3)
    u = np.c_[a, a, a] * units('m/s')
    c = h_convergence(u, u, 1 * units.meter, 1 * units.meter)
    true_c = np.ones_like(u) / units.sec
    assert_array_equal(c, true_c)


def test_advection_uniform():
    """Test advection calculation for a uniform 1D field."""
    u = np.ones((3,)) * units('m/s')
    s = np.ones_like(u) * units.kelvin
    a = advection(s, u, (1 * units.meter,))
    truth = np.zeros_like(u) * units('K/sec')
    assert_array_equal(a, truth)


def test_advection_1d_uniform_wind():
    """Test advection for simple 1D case with uniform wind."""
    u = np.ones((3,)) * units('m/s')
    s = np.array([1, 2, 3]) * units('kg')
    a = advection(s, u, (1 * units.meter,))
    truth = -np.ones_like(u) * units('kg/sec')
    assert_array_equal(a, truth)


def test_advection_1d():
    """Test advection calculation with varying wind and field."""
    u = np.array([1, 2, 3]) * units('m/s')
    s = np.array([1, 2, 3]) * units('Pa')
    a = advection(s, u, (1 * units.meter,))
    truth = np.array([-1, -2, -3]) * units('Pa/sec')
    assert_array_equal(a, truth)


def test_advection_2d_uniform():
    """Test advection for uniform 2D field."""
    u = np.ones((3, 3)) * units('m/s')
    s = np.ones_like(u) * units.kelvin
    a = advection(s, [u, u], (1 * units.meter, 1 * units.meter))
    truth = np.zeros_like(u) * units('K/sec')
    assert_array_equal(a, truth)


def test_advection_2d():
    """Test advection in varying 2D field."""
    u = np.ones((3, 3)) * units('m/s')
    v = 2 * np.ones((3, 3)) * units('m/s')
    s = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]]) * units.kelvin
    a = advection(s, [u, v], (1 * units.meter, 1 * units.meter))
    truth = np.array([[-3, -2, 1], [-4, 0, 4], [-1, 2, 3]]) * units('K/sec')
    assert_array_equal(a, truth)


def test_geostrophic_wind():
    """Test geostrophic wind calculation with basic conditions."""
    z = np.array([[48, 49, 48], [49, 50, 49], [48, 49, 48]]) * 100. * units.meter
    # Using g as the value for f allows it to cancel out
    ug, vg = geostrophic_wind(z, g.magnitude / units.sec,
                              100. * units.meter, 100. * units.meter)
    true_u = np.array([[-1, 0, 1]] * 3) * units('m/s')
    true_v = -true_u.T
    assert_array_equal(ug, true_u)
    assert_array_equal(vg, true_v)


def test_geostrophic_geopotential():
    """Test geostrophic wind calculation with geopotential."""
    z = np.array([[48, 49, 48], [49, 50, 49], [48, 49, 48]]) * 100. * units('m^2/s^2')
    ug, vg = geostrophic_wind(z, 1 / units.sec, 100. * units.meter, 100. * units.meter)
    true_u = np.array([[-1, 0, 1]] * 3) * units('m/s')
    true_v = -true_u.T
    assert_array_equal(ug, true_u)
    assert_array_equal(vg, true_v)


def test_geostrophic_3d():
    """Test geostrophic wind calculation with 3D array."""
    z = np.array([[48, 49, 48], [49, 50, 49], [48, 49, 48]]) * 100.
    # Using g as the value for f allows it to cancel out
    z3d = np.dstack((z, z)) * units.meter
    ug, vg = geostrophic_wind(z3d, g.magnitude / units.sec,
                              100. * units.meter, 100. * units.meter)
    true_u = np.array([[-1, 0, 1]] * 3) * units('m/s')
    true_v = -true_u.T

    true_u = concatenate((true_u[..., None], true_u[..., None]), axis=2)
    true_v = concatenate((true_v[..., None], true_v[..., None]), axis=2)
    assert_array_equal(ug, true_u)
    assert_array_equal(vg, true_v)


def test_geostrophic_gempak():
    """Test of geostrophic wind calculation against gempak values."""
    z = np.array([[5586387.00, 5584467.50, 5583147.50],
                  [5594407.00, 5592487.50, 5591307.50],
                  [5604707.50, 5603247.50, 5602527.50]]).T \
        * (9.80616 * units('m/s^2')) * 1e-3
    dx = np.deg2rad(0.25) * Re * np.cos(np.deg2rad(44))
    # Inverting dy since latitudes in array increase as you go up
    dy = -np.deg2rad(0.25) * Re
    f = (2 * omega * np.sin(np.deg2rad(44))).to('1/s')
    ug, vg = geostrophic_wind(z * units.m, f, dx, dy)
    true_u = np.array([[21.97512, 21.97512, 22.08005],
                       [31.89402, 32.69477, 33.73863],
                       [38.43922, 40.18805, 42.14609]])
    true_v = np.array([[-10.93621, -7.83859, -4.54839],
                       [-10.74533, -7.50152, -3.24262],
                       [-8.66612, -5.27816, -1.45282]])
    assert_almost_equal(ug[1, 1], true_u[1, 1] * units('m/s'), 2)
    assert_almost_equal(vg[1, 1], true_v[1, 1] * units('m/s'), 2)
