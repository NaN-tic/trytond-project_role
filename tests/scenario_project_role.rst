=====================
Project Role Scenario
=====================

Imports::

    >>> from proteus import Model
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company

Install account_invoice::

    >>> config = activate_modules('project_role')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party()
    >>> party.save()

    >>> party2 = Party()
    >>> party2.name = 'emp1'
    >>> party2.save()

    >>> party3 = Party()
    >>> party3.name = 'emp2'
    >>> party3.save()

Create employee::

    >>> Employee = Model.get('company.employee')
    >>> employee1 = Employee()
    >>> employee1.party = party2
    >>> employee1.company = company
    >>> employee1.save()

    >>> employee2 = Employee()
    >>> employee2.party = party3
    >>> employee2.company = company
    >>> employee2.save()

Create Roles::

    >>> Role = Model.get('project.role')
    >>> dev = Role()
    >>> dev.name = 'Developer'
    >>> dev.save()
    >>> tester = Role()
    >>> tester.name = 'Tester'
    >>> tester.save()

Create TaskPhase::

    >>> Task_Phase = Model.get('project.work.task_phase')
    >>> phase = Task_Phase()
    >>> phase.name = 'inici'
    >>> phase.role = dev
    >>> phase.save()
    >>> phase2 = Task_Phase()
    >>> phase2.name = 'test'
    >>> phase2.role = tester
    >>> phase2.save()

Create Workflow::

    >>> Workflow = Model.get('project.work.workflow')
    >>> workflow = Workflow()
    >>> workflow.name = 'workflowTest'
    >>> workflow.save()

Create Workflow Lines ::

    >>> Workflow_Line = Model.get('project.work.workflow.line')
    >>> workflow_line = Workflow_Line()
    >>> workflow_line.workflow = workflow
    >>> workflow_line.phase = phase
    >>> workflow_line.save()

    >>> workflow_line2 = Workflow_Line()
    >>> workflow_line2.workflow = workflow
    >>> workflow_line2.phase = phase2
    >>> workflow_line2.save()

Create Tracker::

    >>> Tracker = Model.get('project.work.tracker')
    >>> tracker = Tracker()
    >>> tracker.name = 'TrackerTest'
    >>> tracker.workflow = workflow
    >>> tracker.save()

Create Task::

    >>> Task = Model.get('project.work')
    >>> task = Task()
    >>> task.name = 'testTask'
    >>> task.company = company
    >>> task.tracker = tracker
    >>> task.task_phase = workflow_line2.phase
    >>> task.state = 'opened'
    >>> task.save()

Create Allocation::

    >>> Allocation = Model.get('project.allocation')
    >>> allocation = Allocation()
    >>> allocation.work = task
    >>> allocation.role = dev
    >>> allocation.employee = employee1
    >>> allocation.save()

    >>> allocation2 = Allocation()
    >>> allocation2.work = task
    >>> allocation2.role = tester
    >>> allocation2.employee = employee2
    >>> allocation2.save()

Searcher ::
    >>> result, = Task.find(['name','ilike', '%test%'])
    >>> result.id == task.id
    True

Searcher Asignee Tests::

    >>> result, = Task.find(['assignee', 'ilike', '%emp2%'])
    >>> result.id == task.id
    True
    >>> result = Task.find(['assignee', 'ilike', '%emp1%'])
    >>> result
    []

Searcher employee/role::

    >>> result, = Task.find(['role_employee', 'ilike', '%emp1/dev%'])
    >>> result.id == task.id
    True
    >>> result, = Task.find(['role_employee', 'ilike', '%emp2/test%'])
    >>> result.id == task.id
    True
    >>> result = Task.find(['role_employee', 'ilike', '%emp1/test%'])
    >>> result
    []
    >>> result, = Task.find(['role_employee', 'ilike', '%emp1%'])
    >>> result.id == task.id
    True
    >>> result = Task.find(['role_employee', 'ilike', '%test%'])
    >>> result
    []
