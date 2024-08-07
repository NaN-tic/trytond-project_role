import unittest

from proteus import Model
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install account_invoice
        config = activate_modules('project_role')

        # Create company
        _ = create_company()
        company = get_company()

        # Get status
        WorkStatus = Model.get('project.work.status')
        open, = WorkStatus.find([('name', '=', "Open")])

        # Create party
        Party = Model.get('party.party')
        party = Party()
        party.save()
        party2 = Party()
        party2.name = 'emp1'
        party2.save()
        party3 = Party()
        party3.name = 'emp2'
        party3.save()

        # Create employee
        Employee = Model.get('company.employee')
        employee1 = Employee()
        employee1.party = party2
        employee1.company = company
        employee1.save()
        employee2 = Employee()
        employee2.party = party3
        employee2.company = company
        employee2.save()

        # Create Roles
        Role = Model.get('project.role')
        dev = Role()
        dev.name = 'Developer'
        dev.save()
        tester = Role()
        tester.name = 'Tester'
        tester.save()
        reviewer = Role()
        reviewer.name = 'Reviewer'
        reviewer.save()

        # Create Status
        Status = Model.get('project.work.status')
        status = Status()
        status.name = 'Start'
        status.role = dev
        status.types = ['task']
        status.save()
        status2 = Status()
        status2.name = 'Test'
        status2.role = tester
        status2.types = ['task']
        status2.save()

        # Create Workflow
        Workflow = Model.get('project.work.workflow')
        workflow = Workflow()
        workflow.name = 'workflow'
        workflow.save()

        # Create Workflow Lines
        WorkflowLine = Model.get('project.work.workflow.line')
        workflow_line = WorkflowLine()
        workflow_line.workflow = workflow
        workflow_line.status = status
        workflow_line.save()
        workflow_line2 = WorkflowLine()
        workflow_line2.workflow = workflow
        workflow_line2.status = status2
        workflow_line2.save()

        # Create Tracker
        Tracker = Model.get('project.work.tracker')
        tracker = Tracker()
        tracker.name = 'Tracker'
        tracker.workflow = workflow
        tracker.save()

        # Create Configuration
        Configuration = Model.get('work.configuration')
        Sequence = Model.get('ir.sequence')
        work_sequence, = Sequence.find([('sequence_type.name', '=', "Work")],
                                       limit=1)
        config = Configuration(1)
        config.default_allocation_employee = employee2
        config.work_sequence = work_sequence
        config.save()

        # Create Project
        Work = Model.get('project.work')
        project = Work()
        project.name = 'Project'
        project.company = company
        project.type = 'project'
        project.status = open
        project.save()
        self.assertEqual(project.allocations, [])

        # Create Allocation
        Allocation = Model.get('project.allocation')
        allocation = Allocation()
        allocation.role = dev
        allocation.work = project
        allocation.employee = employee1
        allocation.save()

        # Create Task
        task = Work()
        task.type = 'task'
        task.parent = project
        task.name = 'Task'
        task.company = company
        task.tracker = tracker
        task.status = workflow_line2.status
        task.save()

        # Searcher
        result, = Work.find(['name', 'ilike', '%Tas%'])
        self.assertEqual(result, task)

        # Searcher Asignee Tests
        result, = Work.find(['assignee', 'ilike', '%emp2%'])
        self.assertEqual(result, task)
        result = Work.find(['assignee', 'ilike', '%emp1%'])
        self.assertEqual(result, [])

        # Searcher employee/role
        result = Work.find(['role_employee', 'ilike', '%emp1/dev%'],
                           order=[('id', 'ASC')])
        self.assertEqual(result, [project, task])
        result, = Work.find(['role_employee', 'ilike', '%emp2/test%'])
        self.assertEqual(result, task)
        result = Work.find(['role_employee', 'ilike', '%emp1/test%'])
        self.assertEqual(result, [])
        result = Work.find(['role_employee', 'ilike', '%emp1%'],
                           order=[('id', 'ASC')])
        self.assertEqual(result, [project, task])
        result = Work.find(['role_employee', 'ilike', '%test%'])
        self.assertEqual(result, [])

        # On_change_parent test
        task.allocations[0].employee = employee2
        task.save()
        result = Work.find(['role_employee', 'ilike', '%emp1/dev%'])
        self.assertEqual(result, [project])
        task.parent = None
        task.save()
        task.parent = project
        task.save()
        result = Work.find(['role_employee', 'ilike', '%emp1/dev%'],
                           order=[('id', 'ASC')])
        self.assertEqual(result, [project, task])
        allocation2 = Allocation()
        allocation2.role = reviewer
        allocation2.employee = employee2
        allocation2.work = task
        allocation2.save()
        result, = Work.find(['role_employee', 'ilike', '%emp2/revi%'])
        self.assertEqual(result, task)
        task.parent = None
        task.save()
        task.parent = project
        task.save()
        result, = Work.find(['role_employee', 'ilike', '%emp2/revi%'])
        self.assertEqual(result, task)
        task.allocations[0].delete()
        task.save()
        result = Work.find(['role_employee', 'ilike', '%emp1/dev%'],
                           order=[('id', 'ASC')])
        self.assertEqual(result, [project])
        task.parent = None
        task.save()
        task.parent = project
        task.save()
        result = Work.find(['role_employee', 'ilike', '%emp1/dev%'],
                           order=[('id', 'ASC')])
        self.assertEqual(result, [project, task])
