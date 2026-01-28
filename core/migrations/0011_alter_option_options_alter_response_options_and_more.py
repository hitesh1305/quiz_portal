# core/migrations/0011_...py

from django.db import migrations, models
import django.db.models.deletion # Ensure this is imported if needed by other operations
from django.db.models import Q # Import Q if needed

# ---> ADD THIS FUNCTION <---
def fix_invalid_result_student_references(apps, schema_editor):
    Result = apps.get_model('core', 'Result')
    Student = apps.get_model('core', 'Student')
    db_alias = schema_editor.connection.alias

    # Get IDs of all existing students
    valid_student_ids = set(Student.objects.using(db_alias).values_list('id', flat=True))

    # Find results pointing to non-existent students
    results_to_fix = Result.objects.using(db_alias).exclude(
        Q(student__isnull=True) | Q(student__in=valid_student_ids)
    )

    count = 0
    ids_to_fix = list(results_to_fix.values_list('id', flat=True))
    updated_results = []
    for result_id in ids_to_fix:
         result = Result.objects.using(db_alias).get(id=result_id)
         invalid_id = getattr(result, 'student_id', 'unknown') # Safely get ID for logging
         print(f"  Fixing Result {result.id}: Setting student from invalid ID {invalid_id} to NULL.")
         result.student = None # Set the ForeignKey relationship to None
         updated_results.append(result)
         count += 1

    if updated_results:
        for r in updated_results:
             r.save(update_fields=['student']) # Use field name in update_fields

    if count > 0:
        print(f"  Fixed {count} invalid Result.student references.")
    else:
        print("  No invalid Result.student references found to fix.")
# --------------------------


class Migration(migrations.Migration):

    dependencies = [
        # Make sure this points to your previous migration (e.g., 0010)
        ('core', '0010_alter_question_correct_answer'),
    ]

    operations = [
        # ---> INSERT THE DATA FIX OPERATION HERE (at the beginning) <---
        migrations.RunPython(fix_invalid_result_student_references, migrations.RunPython.noop),

        # The original operation(s) from this file follow:
        # Example:
        migrations.AlterModelOptions(
            name='option',
            options={'ordering': ['order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='response',
            options={'ordering': ['timestamp']},
        ),
        # ... potentially many other AlterField, AddConstraint, etc. operations ...
    ]