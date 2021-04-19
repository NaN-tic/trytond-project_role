# This file is part project_role module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import role

def register():
    Pool.register(
        role.WorkConfiguration,
        role.Role,
        role.Allocation,
        role.WorkStatus,
        role.Work,
        module='project_role', type_='model')
