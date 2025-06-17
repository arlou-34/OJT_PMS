from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv

from .models import Student, Report, ArchivedReport, Evaluation
from django.contrib.auth.models import Group, User
from .models import Student, ArchivedStudent

# Unregister default auth models
admin.site.unregister(Group)
admin.site.unregister(User)

# Customize admin site titles
admin.site.site_header = "OJT Placement Management System"
admin.site.site_title = "OJT Placement Management System"
admin.site.index_title = "Welcome to the OJT Management Dashboard"



@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'id_number', 'get_full_name', 'time_of_log',
        'program', 'academic_year', 'company_placement',
        'company_address', 'designated', 'ojt_start', 'ojt_end',
    )
    search_fields = (
        'id_number', 'last_name', 'first_name', 'program',
        'academic_year', 'company_placement', 'company_address'
    )
    list_filter = ('program', 'company_placement', 'academic_year')
    actions = ['export_as_csv']

    def get_full_name(self, obj):
        return f"{obj.last_name}, {obj.first_name} {obj.middle_name}"
    get_full_name.short_description = 'Full Name'

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=students.csv'

        writer = csv.writer(response)
        writer.writerow([
            'ID Number', 'Full Name', 'Program', 'Academic Year',
            'Company Placement', 'Company Address', 'OJT Start', 'OJT End'
        ])

        for student in queryset:
            writer.writerow([
                student.id_number,
                f"{student.last_name}, {student.first_name} {student.middle_name}",
                student.program,
                student.academic_year,
                student.company_placement,
                student.company_address,
                student.ojt_start,
                student.ojt_end
            ])

        return response
    export_as_csv.short_description = "Export selected students to CSV"

    def delete_model(self, request, obj):
        self.archive_student(obj)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.archive_student(obj)
        super().delete_queryset(request, queryset)

    def archive_student(self, obj):
        ArchivedStudent.objects.create(
            id_number=obj.id_number,
            full_name=f"{obj.last_name}, {obj.first_name} {obj.middle_name or ''}".strip(),
            program=obj.program,
            academic_year=obj.academic_year,
            barangay=obj.barangay,
            municipality=obj.municipality,
            province=obj.province,
            city=obj.city,
            company_placement=obj.company_placement,
            company_address=obj.company_address,
            designated=obj.designated,
            ojt_start=obj.ojt_start,
            ojt_end=obj.ojt_end,
            total_hours=obj.total_hours
        )

@admin.register(ArchivedStudent)
class ArchivedStudentAdmin(admin.ModelAdmin):
    list_display = ('id_number', 'full_name', 'program', 'academic_year', 'company_placement', 'archived_at')
    search_fields = ('id_number', 'full_name', 'program')
    list_filter = ('program', 'academic_year', 'archived_at')
    actions = ['export_as_csv']  # Add the CSV export action

    def export_as_csv(self, request, queryset):
        from django.http import HttpResponse
        import csv

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=archived_students.csv'

        writer = csv.writer(response)
        writer.writerow([
            'ID Number', 'Full Name', 'Program', 'Academic Year',
            'Company Placement', 'Company Address', 'Barangay',
            'Municipality', 'Province', 'City', 'Designated',
            'OJT Start', 'OJT End', 'Total Hours'
        ])

        for student in queryset:
            writer.writerow([
                student.id_number,
                student.full_name,
                student.program,
                student.academic_year,
                student.company_placement,
                student.company_address,
                student.barangay,
                student.municipality,
                student.province,
                student.city,
                student.designated,
                student.ojt_start,
                student.ojt_end,
                student.total_hours
            ])

        return response
    export_as_csv.short_description = "Export selected archived students to CSV"


from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id_number', 'get_full_name', 'get_program', 'download_column', 'uploaded_at')
    search_fields = ('student__id_number', 'student__last_name', 'student__first_name', 'student__program')
    list_filter = ('student__id_number', 'uploaded_at')
    actions = ['export_as_csv']

    def id_number(self, obj):
        return obj.student.id_number
    id_number.short_description = 'ID Number'

    def get_full_name(self, obj):
        return f"{obj.student.last_name}, {obj.student.first_name} {obj.student.middle_name}"
    get_full_name.short_description = 'Full Name'

    def get_program(self, obj):
        return obj.student.program
    get_program.short_description = 'Program'

    def download_column(self, obj):
        links = []
        if obj.file:
            links.append(f'<a href="{obj.file.url}" download style="color:lightblue;text-decoration: none;">Download File</a>')
        if obj.link:
            links.append(f'<a href="{obj.link}" target="_blank" style="color:green;text-decoration: none;">Open Link</a>')
        return format_html("<br>".join(links)) if links else "-"
    download_column.short_description = 'Report Access'

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reports.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID Number', 'Full Name', 'Program', 'Uploaded At', 'File URL', 'Link'])

        for report in queryset:
            writer.writerow([
                report.student.id_number,
                f"{report.student.last_name}, {report.student.first_name} {report.student.middle_name}",
                report.student.program,
                report.uploaded_at,
                report.file.url if report.file else '',
                report.link if report.link else '',
            ])
        return response
    export_as_csv.short_description = "Export Selected to CSV"




    def delete_model(self, request, obj):
        self.archive_report(obj)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.archive_report(obj)
        super().delete_queryset(request, queryset)

    def archive_report(self, obj):
        ArchivedReport.objects.create(
            student_id=obj.student.id_number,
            full_name=obj.student.full_name,
            uploaded_at=obj.uploaded_at,
        )


@admin.register(ArchivedReport)
class ArchivedReportAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'uploaded_at', 'archived_at')
    list_filter = ('uploaded_at', 'archived_at')
    search_fields = ('student_id', 'full_name')
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=archived_reports.csv'

        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Full Name', 'Uploaded At', 'Archived At'])

        for report in queryset:
            writer.writerow([
                report.student_id,
                report.full_name,
                report.uploaded_at,
                report.archived_at
            ])
        return response

    export_as_csv.short_description = "Export selected archived reports to CSV"





from .models import Evaluation, ArchivedEvaluation

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'student_id_number', 'student_full_name', 'evaluator_name',
        'company', 'final_grade', 'letter_grade', 'date_evaluated'
    )
    search_fields = ('student__last_name', 'student__id_number', 'evaluator_name', 'company')
    list_filter = ('date_evaluated', 'company')
    actions = ['export_as_csv']

    def student_full_name(self, obj):
        return f"{obj.student.last_name}, {obj.student.first_name}"
    student_full_name.short_description = 'Student Name'

    def student_id_number(self, obj):
        return obj.student.id_number
    student_id_number.short_description = 'ID Number'

    def letter_grade(self, obj):
        return obj.get_letter_grade()
    letter_grade.short_description = 'College Grade'

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=evaluations.csv'
        writer = csv.writer(response)
        writer.writerow([
            'ID Number', 'Full Name', 'Evaluator Name', 'Company',
            'Punctuality', 'Work Quality', 'Communication Skills',
            'Teamwork', 'Final Grade', 'Letter Grade', 'Comments', 'Date Evaluated'
        ])
        for obj in queryset:
            writer.writerow([
                obj.student.id_number,
                f"{obj.student.last_name}, {obj.student.first_name}",
                obj.evaluator_name,
                obj.company,
                obj.punctuality,
                obj.work_quality,
                obj.communication_skills,
                obj.teamwork,
                obj.final_grade,
                obj.get_letter_grade(),
                obj.comments,
                obj.date_evaluated
            ])
        return response
    export_as_csv.short_description = "Export Selected to CSV"

    def delete_model(self, request, obj):
        self.archive_evaluation(obj)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.archive_evaluation(obj)
        super().delete_queryset(request, queryset)

    def archive_evaluation(self, obj):
        ArchivedEvaluation.objects.create(
            student_id_number=obj.student.id_number,
            student_full_name=f"{obj.student.last_name}, {obj.student.first_name}",
            evaluator_name=obj.evaluator_name,
            company=obj.company,
            punctuality=obj.punctuality,
            work_quality=obj.work_quality,
            communication_skills=obj.communication_skills,
            teamwork=obj.teamwork,
            final_grade=obj.final_grade,
            letter_grade=obj.get_letter_grade(),
            comments=obj.comments,
            date_evaluated=obj.date_evaluated
        )

@admin.register(ArchivedEvaluation)
class ArchivedEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'student_id_number', 'student_full_name', 'evaluator_name', 'company',
        'final_grade', 'letter_grade', 'date_evaluated', 'archived_at'
    )
    search_fields = ('student_id_number', 'student_full_name', 'evaluator_name', 'company')
    list_filter = ('company', 'date_evaluated', 'archived_at')
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=archived_evaluations.csv'
        writer = csv.writer(response)

        writer.writerow([
            'ID Number', 'Full Name', 'Evaluator Name', 'Company',
            'Punctuality', 'Work Quality', 'Communication Skills',
            'Teamwork', 'Final Grade', 'Letter Grade', 'Comments',
            'Date Evaluated', 'Archived At'
        ])

        for obj in queryset:
            writer.writerow([
                obj.student_id_number,
                obj.student_full_name,
                obj.evaluator_name,
                obj.company,
                obj.punctuality,
                obj.work_quality,
                obj.communication_skills,
                obj.teamwork,
                obj.final_grade,
                obj.letter_grade,
                obj.comments,
                obj.date_evaluated,
                obj.archived_at
            ])

        return response

    export_as_csv.short_description = "Export Selected to CSV"
