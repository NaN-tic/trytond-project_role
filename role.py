from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, ModelSQL, fields

__all__ = ['Role', 'Allocation', 'TaskPhase', 'Work']


class Role(ModelSQL, ModelView):
    'Project Role'
    __name__ = 'project.role'
    name = fields.Char('name', required=True)


class Allocation(metaclass=PoolMeta):
    __name__ = 'project.allocation'
    role = fields.Many2One('project.role', "Role")


class TaskPhase(metaclass=PoolMeta):
    __name__= 'project.work.task_phase'
    role = fields.Many2One('project.role', "Role")


class Work(metaclass=PoolMeta):
    __name__ = 'project.work'
    assignee = fields.Function(fields.Many2One('company.employee',
            'Assignee'), 'get_assignee',
            searcher='search_assignee')

    role_employee = fields.Function(fields.Char('Role Employee'),
            'get_role_employee', searcher='search_role_employee')

    def get_assignee(self, name):
        role_need = self.task_phase.role
        for allocation in self.allocations:
            if allocation.role == role_need:
                return allocation.employee.id
        return None

    @classmethod
    def search_assignee(cls, name, clause):
        pool = Pool()
        Allocation = pool.get('project.allocation')
        Phase = pool.get('project.work.task_phase')
        Employee = pool.get('company.employee')
        Party = pool.get('party.party')

        work = cls.__table__()
        allocation = Allocation.__table__()
        phase = Phase.__table__()
        employee = Employee.__table__()
        party = Party.__table__()

        Operator = fields.SQL_OPERATORS[clause[1]]
        join1 = work.join(allocation, condition = work.id == allocation.work)
        join2 = join1.join(phase, condition = phase.id == work.task_phase)
        join3 = join2.join(employee, condition = allocation.employee == employee.id)
        join4 = join3.join(party, condition = party.id == employee.party)
        query = join4.select(work.id)
        query.where = (phase.role == allocation.role) & Operator(party.name, clause[2])
        return [('id', 'in', query)]

    def get_role_employee(self, name):
        res = []
        for allocation in self.allocations:
            res.append('%s/%s' % (allocation.employee.rec_name,
                    allocation.role.rec_name))
        return ' '.join(res)

    @classmethod
    def search_role_employee(cls, name, clause):
        pool = Pool()
        Allocation = pool.get('project.allocation')
        Employee = pool.get('company.employee')
        Party = pool.get('party.party')
        Role = pool.get('project.role')
        work = cls.__table__()
        allocation = Allocation.__table__()
        employee = Employee.__table__()
        party = Party.__table__()
        role = Role.__table__()

        Operator = fields.SQL_OPERATORS[clause[1]]
        value = clause[2]
        values = value.split('/')

        employee_value = values[0]
        if len(values) > 1:
            role_value = values[1]
        else:
            role_value = ''

        if 'like' in clause[1]:
            employee_value = employee_value + '%'
            if role:
                role_value = '%' + role_value

        join = work.join(allocation, condition = work.id == allocation.work)
        join = join.join(employee, condition = allocation.employee == employee.id)
        join = join.join(party, condition = party.id == employee.party)
        if role:
            join = join.join(role, condition = allocation.role == role.id)
        query = join.select(work.id)
        query.where = Operator(party.name, employee_value)
        if role:
            query.where &= Operator(role.name, role_value)
        return [('id', 'in', query)]
