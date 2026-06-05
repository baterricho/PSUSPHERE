import random
from datetime import date, timedelta
from itertools import product

from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from studentorg.models import College, OrgMember, Organization, Program, Student


COLLEGE_DATA = [
    (
        "College of Computing Sciences",
        [
            "Bachelor of Science in Information Technology",
            "Bachelor of Science in Computer Science",
            "Bachelor of Science in Information Systems",
        ],
        [
            (
                "Junior Philippine Computer Society",
                "A community for computing students focused on programming, systems, and technology leadership.",
            ),
            (
                "PSU Tech Innovators",
                "Student organization for software projects, hackathons, and applied digital solutions.",
            ),
        ],
    ),
    (
        "College of Teacher Education",
        [
            "Bachelor of Elementary Education",
            "Bachelor of Secondary Education Major in English",
            "Bachelor of Secondary Education Major in Mathematics",
        ],
        [
            (
                "Future Educators Society",
                "Academic organization for pre-service teachers and education student leaders.",
            ),
            (
                "English Language Circle",
                "Student group for communication, language, and literacy activities.",
            ),
        ],
    ),
    (
        "College of Business and Accountancy",
        [
            "Bachelor of Science in Business Administration",
            "Bachelor of Science in Accountancy",
            "Bachelor of Science in Entrepreneurship",
        ],
        [
            (
                "Junior Financial Executives",
                "Organization for students interested in finance, entrepreneurship, and business strategy.",
            ),
            (
                "Young Entrepreneurs Club",
                "Student group for enterprise development and campus business activities.",
            ),
        ],
    ),
    (
        "College of Engineering and Architecture",
        [
            "Bachelor of Science in Civil Engineering",
            "Bachelor of Science in Electrical Engineering",
            "Bachelor of Science in Architecture",
        ],
        [
            (
                "Engineering Student Council",
                "Student body supporting engineering activities, competitions, and outreach.",
            ),
            (
                "Architecture Guild",
                "Creative organization for design, drafting, and architecture students.",
            ),
        ],
    ),
    (
        "College of Arts and Sciences",
        [
            "Bachelor of Arts in Communication",
            "Bachelor of Science in Biology",
            "Bachelor of Science in Psychology",
        ],
        [
            (
                "Peer Facilitators Organization",
                "Student group promoting mental health awareness, peer support, and guidance programs.",
            ),
            (
                "Campus Media Society",
                "Organization for students interested in journalism, media production, and campus publication.",
            ),
        ],
    ),
]


class Command(BaseCommand):
    help = "Seed PSUSphere with colleges, programs, organizations, students, and memberships."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing student organization data before seeding.",
        )
        parser.add_argument(
            "--students",
            type=int,
            default=80,
            help="Number of fake students to create. Default: 80.",
        )
        parser.add_argument(
            "--memberships",
            type=int,
            default=160,
            help="Number of organization memberships to create. Default: 160.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=20260605,
            help="Random seed for repeatable fake data. Default: 20260605.",
        )

    def handle(self, *args, **options):
        student_count = options["students"]
        membership_count = options["memberships"]

        if student_count < 1:
            raise CommandError("--students must be at least 1.")

        random.seed(options["seed"])
        fake = Faker("en_PH")
        Faker.seed(options["seed"])

        if options["reset"]:
            self.stdout.write(self.style.WARNING("Deleting existing student organization data..."))
            OrgMember.objects.all().delete()
            Student.objects.all().delete()
            Organization.objects.all().delete()
            Program.objects.all().delete()
            College.objects.all().delete()
        elif self._has_existing_data():
            self.stdout.write(
                self.style.WARNING(
                    "Seed skipped because data already exists. "
                    "Run `python manage.py create_initial_data --reset` to recreate seed data."
                )
            )
            return

        colleges, all_programs, organizations = self._create_school_data()
        students = self._create_students(fake, student_count, all_programs)
        self._create_memberships(membership_count, students, organizations)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
        self.stdout.write(
            self.style.SUCCESS(
                f"Totals: {len(colleges)} colleges, {len(all_programs)} programs, "
                f"{len(organizations)} organizations, {len(students)} students, "
                f"{OrgMember.objects.count()} memberships."
            )
        )

    def _has_existing_data(self):
        return any(
            model.objects.exists()
            for model in (College, Program, Organization, Student, OrgMember)
        )

    def _create_school_data(self):
        colleges = []
        all_programs = []
        organizations = []

        for college_name, program_names, organization_rows in COLLEGE_DATA:
            college = College.objects.create(college_name=college_name)
            colleges.append(college)

            for program_name in program_names:
                program = Program.objects.create(prog_name=program_name, college=college)
                all_programs.append(program)

            for organization_name, description in organization_rows:
                organizations.append(
                    Organization.objects.create(
                        name=organization_name,
                        college=college,
                        description=description,
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"Created {len(colleges)} colleges."))
        self.stdout.write(self.style.SUCCESS(f"Created {len(all_programs)} programs."))
        self.stdout.write(self.style.SUCCESS(f"Created {len(organizations)} organizations."))
        return colleges, all_programs, organizations

    def _create_students(self, fake, count, programs):
        students = []

        for index in range(1, count + 1):
            admission_year = random.randint(2020, 2026)
            student_id = f"{admission_year}-{index:05d}"
            first_name = fake.first_name()
            last_name = fake.last_name()
            middle_name = fake.last_name() if random.random() < 0.8 else ""

            students.append(
                Student.objects.create(
                    student_id=student_id,
                    lastname=last_name[:25],
                    firstname=first_name[:25],
                    middlename=middle_name[:25],
                    program=random.choice(programs),
                )
            )

        self.stdout.write(self.style.SUCCESS(f"Created {len(students)} students."))
        return students

    def _create_memberships(self, count, students, organizations):
        possible_pairs = list(product(students, organizations))
        max_memberships = len(possible_pairs)

        if count > max_memberships:
            self.stdout.write(
                self.style.WARNING(
                    f"Requested {count} memberships, but only {max_memberships} unique pairs are possible."
                )
            )
            count = max_memberships

        selected_pairs = random.sample(possible_pairs, count)

        for student, organization in selected_pairs:
            days_back = random.randint(1, 900)
            OrgMember.objects.create(
                student=student,
                organization=organization,
                date_joined=date.today() - timedelta(days=days_back),
            )

        self.stdout.write(self.style.SUCCESS(f"Created {len(selected_pairs)} memberships."))
