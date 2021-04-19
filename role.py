from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, ModelSQL, fields


class Role(ModelSQL, ModelView):
    'Project Role'
    __name__ = 'project.role'
    name = fields.Char('name', required=True)


class WorkConfiguration(metaclass=PoolMeta):
    __name__ = 'work.configuration'
    default_allocation_employee = fields.Many2One('company.employee',
        'Default Allocation Employee')


class Allocation(metaclass=PoolMeta):
    __name__ = 'project.allocation'
    role = fields.Many2One('project.role', "Role", required=True)


class WorkStatus(metaclass=PoolMeta):
    __name__= 'project.work.status'
    role = fields.Many2One('project.role', "Role")


class Work(metaclass=PoolMeta):
    __name__ = 'project.work'
    assignee = fields.Function(fields.Many2One('company.employee',
            'Assignee'), 'get_assignee',
            searcher='search_assignee')
    role_employee = fields.Function(fields.Char('Role Employee'),
            'get_role_employee', searcher='search_role_employee')

    @fields.depends('parent', 'allocations', '_parent_parent.id')
    def on_change_parent(self):
        pool = Pool()
        Allocation = pool.get('project.allocation')
        # try except needed cause super don't have on_change_parent
        # but it could have it in the future
        try:
            super(Work, self).on_change_parent()
        except:
            pass
        if not self.parent or not self.parent.allocations:
            return
        allocations =[]
        for allocation_parent in self.parent.allocations:
            for allocation in self.allocations:
                if allocation_parent.role == allocation.role:
                    allocation.employee = allocation_parent.employee
                    break
            else:
                new_allocation = Allocation()
                new_allocation.role = allocation_parent.role
                new_allocation.employee = allocation_parent.employee
                allocations.append(new_allocation)
        self.allocations += tuple(allocations)

    @fields.depends('tracker', 'allocations')
    def on_change_tracker(self):
        pool = Pool()
        Allocation = pool.get('project.allocation')
        Configuration = Pool().get('work.configuration')
        # try except needed cause super doesn't have on_change_tracker
        # but it could have it in the future
        try:
            super(Work, self).on_change_tracker()
        except:
            pass
        if not self.tracker or not self.tracker.workflow:
            return
        allocations = []
        existing_roles = {x.role for x in self.allocations if x.role}
        for line in self.tracker.workflow.lines:
            role = line.status.role
            if not role or role in existing_roles:
                continue
            existing_roles.add(role)
            allocation = Allocation()
            allocation.role = role
            allocation.employee = Configuration(1).default_allocation_employee
            allocations.append(allocation)
        self.allocations += tuple(allocations)


    @classmethod
    def _get_assignee_query(cls):
        pool = Pool()
        Allocation = pool.get('project.allocation')
        Status = pool.get('project.work.status')
        Employee = pool.get('company.employee')
        Party = pool.get('party.party')
        Role = pool.get('project.role')

        work = cls.__table__()
        allocation = Allocation.__table__()
        status = Status.__table__()
        employee = Employee.__table__()
        party = Party.__table__()
        role = Role.__table__()

        join1 = work.join(allocation, condition = work.id == allocation.work)
        join2 = join1.join(status, condition = status.id == work.status)
        join3 = join2.join(employee, condition = allocation.employee == employee.id)
        join4 = join3.join(party, condition = party.id == employee.party)
        join5 = join4.join(role, condition = allocation.role == role.id)
        query = join5.select(work.id)
        query.where = (status.role == allocation.role)
        return query, party, role

    def get_assignee(self, name):
        if not self.status:
            return
        role_need = self.status.role
        for allocation in self.allocations:
            if allocation.role == role_need:
                return allocation.employee.id

    @classmethod
    def search_assignee(cls, name, clause):
        query, party, _ = cls._get_assignee_query()
        Operator = fields.SQL_OPERATORS[clause[1]]
        query.where &= (Operator(party.name, clause[2]))
        return [('id', 'in', query)]

    def get_role_employee(self, name):
        res = []
        for allocation in self.allocations:
            res.append('%s/%s' % (allocation.employee.rec_name,
                    allocation.role.rec_name if allocation.role else ''))
        return ' '.join(res)

    @classmethod
    def search_role_employee(cls, name, clause):
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
            if role_value:
                role_value = '%' + role_value

        query, party, role = cls._get_assignee_query()

        if role_value:
            query.where = (Operator(role.name, role_value)
                & Operator(party.name, employee_value))
        else:
            query.where = Operator(party.name, employee_value)

        return [('id', 'in', query)]
