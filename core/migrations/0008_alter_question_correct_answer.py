# core/migrations/0008_alter_question_correct_answer.py

from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


def set_invalid_correct_answers_to_null(apps, schema_editor):
    Question = apps.get_model('core', 'Question')
    Option = apps.get_model('core', 'Option')
    db_alias = schema_editor.connection.alias

    valid_option_ids = set(Option.objects.using(db_alias).values_list('id', flat=True))

    questions_to_fix = Question.objects.using(db_alias).exclude(
        Q(correct_answer__isnull=True) | Q(correct_answer__in=valid_option_ids)
    )

    count = 0
    ids_to_fix = list(questions_to_fix.values_list('id', flat=True))
    updated_questions = []
    for question_id in ids_to_fix:
         question = Question.objects.using(db_alias).get(id=question_id)
         # --- FIX: Use the field name 'correct_answer' ---
         # Get the current invalid ID for logging *before* setting to None
         invalid_id = getattr(question, 'correct_answer_id', 'unknown') # Safely get ID if possible
         print(f"  Fixing Question {question.id}: Setting correct_answer from invalid ID {invalid_id} to NULL.")
         question.correct_answer = None # Set the ForeignKey relationship to None
         updated_questions.append(question)
         # ---------------------------------------------
         count += 1

    if updated_questions:
        for q in updated_questions:
             # --- FIX: Use the field name in update_fields ---
             q.save(update_fields=['correct_answer'])
             # ---------------------------------------------

    if count > 0:
        print(f"  Fixed {count} invalid correct_answer references.")
    else:
        print("  No invalid correct_answer references found to fix.")


class Migration(migrations.Migration):

    dependencies = [
        # Ensure this matches your ACTUAL previous migration name
        ('core', '0007_alter_option_order_alter_option_question_and_more'),
    ]

    operations = [
        migrations.RunPython(set_invalid_correct_answers_to_null, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='question',
            name='correct_answer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='correct_for_question', to='core.option'),
        ),
    ]