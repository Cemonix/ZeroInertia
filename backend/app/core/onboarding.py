"""User onboarding utilities for creating tutorial content."""
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.project import Project
from app.models.section import Section
from app.models.task import Task


async def create_tutorial_project(session: AsyncSession, user_id: UUID) -> Project:
    """Create tutorial project with sample tasks for new users.

    Args:
        session: Database session to use
        user_id: ID of the user to create tutorial for

    Returns:
        Created tutorial project
    """
    logger.info(f"Creating tutorial project for user {user_id}")

    tutorial_project = Project(
        id=uuid4(),
        title="🎓 Getting Started with Zero Inertia",
        order_index=0,
        is_inbox=False,
        user_id=user_id,
        parent_id=None
    )
    session.add(tutorial_project)
    await session.flush()

    basics_section = Section(
        id=uuid4(),
        title="The Basics",
        project_id=tutorial_project.id,
        user_id=user_id,
        order_index=0
    )
    organization_section = Section(
        id=uuid4(),
        title="Projects & Organization",
        project_id=tutorial_project.id,
        user_id=user_id,
        order_index=1
    )
    advanced_section = Section(
        id=uuid4(),
        title="Advanced Features",
        project_id=tutorial_project.id,
        user_id=user_id,
        order_index=2
    )
    session.add_all([basics_section, organization_section, advanced_section])
    await session.flush()

    tutorial_tasks = [
        Task(
            id=uuid4(),
            title="✅ Welcome to Zero Inertia!",
            description=(
                "Welcome to your personal productivity system! 🎉\n\n"
                "**What is Zero Inertia?**\n"
                "Zero Inertia is your \"second brain\" - a unified system for managing tasks, "
                "tracking achievements, organizing knowledge, and visualizing your progress.\n\n"
                "**Getting Started:**\n"
                "- Complete the tasks in this tutorial to learn the basics\n"
                "- Each task contains instructions and tips\n"
                "- Feel free to edit, complete, or delete these tasks - they're yours!\n\n"
                "**Quick Tip:** Click this task to open it and see all details. "
                "Check the box to mark it complete! ✓"
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=basics_section.id,
            order_index=0,
            completed=False,
            archived=False
        ),
        Task(
            id=uuid4(),
            title="Try setting a due date",
            description=(
                "**Due dates** help you stay on track with deadlines.\n\n"
                "**How to add a due date:**\n"
                "1. Click this task to open the task modal\n"
                "2. Click the date/time button in the toolbar\n"
                "3. Pick a date and optional time\n\n"
                "**Pro Tip:** You can use natural language! Type `@ tomorrow` or "
                "`@ next friday 3pm` in the title field, and the date will be detected automatically. "
                "The @ symbol and date text will be removed when you save."
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=basics_section.id,
            order_index=1,
            completed=False,
            archived=False
        ),
        Task(
            id=uuid4(),
            title="Add a priority to this task",
            description=(
                "**Priorities** help you focus on what matters most.\n\n"
                "**Available priorities:**\n"
                "- 🔵 Low - Can wait\n"
                "- 🟡 Medium - Should do soon\n"
                "- 🟠 High - Important\n"
                "- 🔴 Urgent - Do now!\n\n"
                "**Try it:** Open this task and select a priority from the dropdown."
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=basics_section.id,
            order_index=2,
            completed=False,
            archived=False
        ),
        Task(
            id=uuid4(),
            title="Write a task description",
            description=(
                "Task descriptions support **Markdown formatting**! 🎨\n\n"
                "**You can use:**\n"
                "- **Bold** and *italic* text\n"
                "- Bullet lists (like this one)\n"
                "- `Code blocks`\n"
                "- Links and more\n\n"
                "**Try it:** Click \"Edit\" and add your own description to this task. "
                "Experiment with the formatting!"
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=basics_section.id,
            order_index=3,
            completed=False,
            archived=False
        ),
        Task(
            id=uuid4(),
            title="Create your first custom project",
            description=(
                "**Projects** help organize related tasks together.\n\n"
                "**Examples:**\n"
                "- 💼 Work projects\n"
                "- 🏠 Home & personal\n"
                "- 📚 Learning & courses\n"
                "- 🎯 Goals & habits\n\n"
                "**Try it:**\n"
                "1. Look at the left sidebar\n"
                "2. Click the \"+\" button next to \"Projects\"\n"
                "3. Name your project and pick a color\n\n"
                "Projects can also have sub-projects for deeper organization!"
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=organization_section.id,
            order_index=0,
            completed=False,
            archived=False
        ),
        Task(
            id=uuid4(),
            title="Try the Board view",
            description=(
                "**Board view** gives you a Kanban-style layout of your project.\n\n"
                "**How to use it:**\n"
                "1. Click on any project in the left sidebar\n"
                "2. Switch to \"Board\" view (button at the top)\n"
                "3. Drag tasks between sections to organize them\n\n"
                "**Sections** act as columns in board view - perfect for workflows like:\n"
                "- To Do → In Progress → Done\n"
                "- Backlog → This Week → Completed\n"
                "- Ideas → Planning → Executing"
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=organization_section.id,
            order_index=1,
            completed=False,
            archived=False
        ),
        Task(
            id=uuid4(),
            title="Organize with sections",
            description=(
                "**Sections** help divide projects into logical groups.\n\n"
                "**Try it:**\n"
                "1. Open any project\n"
                "2. Click \"Add Section\" button\n"
                "3. Give it a name\n"
                "4. Drag tasks into different sections\n\n"
                "**Use cases:**\n"
                "- Phase 1, Phase 2, Phase 3\n"
                "- Categories: Research, Development, Testing\n"
                "- Status: Not Started, Active, Complete"
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=organization_section.id,
            order_index=2,
            completed=False,
            archived=False
        ),
        Task(
            id=uuid4(),
            title="Try adding labels",
            description=(
                "**Labels** let you categorize and filter tasks across projects.\n\n"
                "**Examples:**\n"
                "- 🏷️ @work, @home, @errands\n"
                "- ⏱️ 5min, 30min, 2hours\n"
                "- 👤 @person-name for delegated tasks\n\n"
                "**Try it:**\n"
                "1. Open this task\n"
                "2. Click the \"Label\" button\n"
                "3. Create a new label or select existing ones\n"
                "4. Add multiple labels to one task\n\n"
                "**Pro tip:** Use labels to filter your view and find tasks quickly!"
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=advanced_section.id,
            order_index=0,
            completed=False,
            archived=False
        ),
        Task(
            id=uuid4(),
            title="Set up a recurring task",
            description=(
                "**Recurring tasks** automatically recreate themselves on a schedule.\n\n"
                "**Perfect for:**\n"
                "- Daily habits (exercise, journaling)\n"
                "- Weekly routines (meal planning, reviews)\n"
                "- Monthly tasks (bills, reports)\n\n"
                "**Try it:**\n"
                "1. Open this task (make sure it has a due date first!)\n"
                "2. Click the \"Repeat\" button\n"
                "3. Choose frequency: daily, weekly, monthly, or yearly\n"
                "4. Customize the pattern (e.g., \"every 2 weeks on Monday and Friday\")\n\n"
                "**Note:** When you complete a recurring task, a new instance is created automatically!"
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=advanced_section.id,
            order_index=1,
            completed=False,
            archived=False
        ),
        Task(
            id=uuid4(),
            title="Add a checklist to break down tasks",
            description=(
                "**Checklists** help break large tasks into smaller steps.\n\n"
                "**Try it:**\n"
                "1. Open this task\n"
                "2. Click the \"Checklist\" button\n"
                "3. Add a title like \"Steps\"\n"
                "4. Add individual items to check off\n\n"
                "**Use cases:**\n"
                "- Multi-step procedures\n"
                "- Packing lists\n"
                "- Quality assurance checks\n"
                "- Recipe steps\n\n"
                "You can add multiple checklists to one task and reorder items with drag-and-drop!"
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=advanced_section.id,
            order_index=2,
            completed=False,
            archived=False
        ),
        Task(
            id=uuid4(),
            title="Explore the Calendar and Today view",
            description=(
                "**Calendar view** helps you visualize tasks over time.\n\n"
                "**Features:**\n"
                "- See all tasks with due dates\n"
                "- Drag and drop to reschedule\n"
                "- Track your completion streak 🔥\n"
                "- View daily, weekly, or monthly\n\n"
                "**Try it:**\n"
                "1. Click \"Today\" in the left sidebar\n"
                "2. Check your streak counter\n"
                "3. Try different calendar views (day/week/month)\n"
                "4. Click on dates to see tasks\n\n"
                "**Pro tip:** Complete tasks daily to maintain your streak and stay motivated!"
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=advanced_section.id,
            order_index=3,
            completed=False,
            archived=False
        ),
        Task(
            id=uuid4(),
            title="🎉 You're ready to go!",
            description=(
                "Congratulations! You now know the core features of Zero Inertia. 🚀\n\n"
                "**Next Steps:**\n"
                "- Create your own projects and tasks\n"
                "- Explore the Media Tracker (books, movies, games, courses)\n"
                "- Try the Notes feature for your knowledge base\n"
                "- Build your daily task completion streak\n\n"
                "**Remember:**\n"
                "- You can delete or archive this tutorial project anytime\n"
                "- Use the Inbox for quick task capture\n"
                "- Organize into projects as you go\n"
                "- Review your progress in the Statistics view\n\n"
                "**Tip:** The best productivity system is the one you actually use. "
                "Start simple, and add complexity as needed. Good luck! 💪"
            ),
            user_id=user_id,
            project_id=tutorial_project.id,
            section_id=advanced_section.id,
            order_index=4,
            completed=False,
            archived=False
        ),
    ]
    session.add_all(tutorial_tasks)
    await session.commit()

    logger.info(f"Created tutorial project with {len(tutorial_tasks)} tasks for user {user_id}")
    return tutorial_project
