"""
Assessment Serializers for CAAS Platform

TEACHING MOMENT: These serializers handle the complex relationships between
templates, questions, assessments, and responses. It's like managing a whole
testing system - from creating exams to grading them!
"""

from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import AssessmentTemplate, Question, Assessment, AssessmentResponse
from apps.vendors.serializers import VendorListSerializer


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for assessment questions.
    
    TEACHING: Questions can have different types, so we validate
    that the data matches the question type (e.g., choices for multiple choice).
    """
    
    class Meta:
        model = Question
        fields = [
            'id',
            'question_text',
            'help_text',
            'question_type',
            'choices',
            'points',
            'correct_answer',
            'section',
            'order',
            'is_required',
            'is_critical',
        ]
    
    def validate(self, data):
        """
        Ensure question data matches its type.
        
        TEACHING: Different question types need different data:
        - Multiple choice needs choices
        - Yes/No needs a boolean correct answer
        - Text questions don't need correct answers (manual review)
        """
        question_type = data.get('question_type')
        
        if question_type == 'multiple_choice' and not data.get('choices'):
            raise serializers.ValidationError({
                'choices': 'Multiple choice questions must have choices'
            })
        
        if question_type == 'yes_no' and data.get('correct_answer') not in ['yes', 'no', None]:
            raise serializers.ValidationError({
                'correct_answer': 'Yes/No questions must have "yes" or "no" as correct answer'
            })
        
        return data


class AssessmentTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for assessment templates with nested questions.
    
    TEACHING: This uses nested serialization - when you get a template,
    you also get all its questions. It's like getting a complete exam paper.
    """
    
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    organization_name = serializers.CharField(
        source='organization.name',
        read_only=True
    )
    created_by_name = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    
    class Meta:
        model = AssessmentTemplate
        fields = [
            'id',
            'name',
            'description',
            'assessment_type',
            'total_points',
            'passing_score',
            'is_active',
            'organization',
            'organization_name',
            'questions',
            'question_count',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_name',
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_question_count(self, obj):
        """Count total questions in this template"""
        return obj.questions.count()
    
    def create(self, validated_data):
        """
        Create template with automatic organization assignment.
        
        TEACHING: Like with vendors, we auto-assign the organization
        based on the current user's membership.
        """
        user = self.context['request'].user
        validated_data['created_by'] = user
        
        # Get user's organization if not provided
        if 'organization' not in validated_data:
            membership = user.organization_memberships.first()
            if not membership:
                raise serializers.ValidationError(
                    "You must belong to an organization to create templates"
                )
            validated_data['organization'] = membership.organization
        
        return super().create(validated_data)


class AssessmentTemplateCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating templates.
    """
    
    class Meta:
        model = AssessmentTemplate
        fields = [
            'name',
            'description', 
            'assessment_type',
            'total_points',
            'passing_score',
        ]
    
    def create(self, validated_data):
        """
        Create template with automatic organization assignment.
        
        TEACHING: We need to assign the organization based on the current user!
        """
        user = self.context['request'].user
        validated_data['created_by'] = user
        
        # Get user's organization
        membership = user.organization_memberships.first()
        if not membership:
            raise serializers.ValidationError(
                "You must belong to an organization to create templates"
            )
        validated_data['organization'] = membership.organization
        
        return super().create(validated_data)

class AssessmentResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for vendor responses to questions.
    
    TEACHING: This handles the actual answers vendors provide.
    Different question types need different answer formats.
    """
    
    question_text = serializers.CharField(
        source='question.question_text',
        read_only=True
    )
    question_type = serializers.CharField(
        source='question.question_type',
        read_only=True
    )
    question_points = serializers.IntegerField(
        source='question.points',
        read_only=True
    )
    
    class Meta:
        model = AssessmentResponse
        fields = [
            'id',
            'question',
            'question_text',
            'question_type',
            'question_points',
            'answer_text',
            'answer_json',
            'answer_file',
            'points_earned',
            'is_approved',
            'reviewer_comment',
            'answered_at',
        ]
        read_only_fields = ['points_earned', 'is_approved', 'reviewer_comment']
    
    def validate(self, data):
        """
        Validate answer format matches question type.
        """
        if self.instance:  # Update
            question = self.instance.question
        else:  # Create
            question = data.get('question')
        
        if not question:
            return data
        
        answer_text = data.get('answer_text')
        answer_json = data.get('answer_json')
        
        # Validate based on question type
        if question.question_type == 'yes_no':
            if answer_text not in ['yes', 'no']:
                raise serializers.ValidationError({
                    'answer_text': 'Answer must be "yes" or "no"'
                })
        
        elif question.question_type == 'multiple_choice':
            if not answer_json or 'selected' not in answer_json:
                raise serializers.ValidationError({
                    'answer_json': 'Multiple choice must have a selected option'
                })
        
        elif question.question_type == 'number':
            try:
                float(answer_text)
            except (ValueError, TypeError):
                raise serializers.ValidationError({
                    'answer_text': 'Answer must be a valid number'
                })
        
        return data


class AssessmentSerializer(serializers.ModelSerializer):
    """
    Main serializer for assessments with all related data.
    
    TEACHING: This is the complete picture - it shows the assessment,
    the vendor taking it, the template it's based on, and all responses.
    """
    
    vendor = VendorListSerializer(read_only=True)
    template_name = serializers.CharField(
        source='template.name',
        read_only=True
    )
    responses = AssessmentResponseSerializer(many=True, read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Assessment
        fields = [
            'id',
            'template',
            'template_name',
            'vendor',
            'assigned_by',
            'assigned_date',
            'due_date',
            'status',
            'started_date',
            'submitted_date',
            'reviewed_date',
            'reviewed_by',
            'score',
            'passed',
            'reviewer_notes',
            'vendor_notes',
            'responses',
            'completion_percentage',
            'is_overdue',
            'days_until_due',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'assigned_by', 'assigned_date', 'started_date',
            'submitted_date', 'reviewed_date', 'score', 'passed'
        ]
    
    def get_completion_percentage(self, obj):
        """
        Calculate how much of the assessment is complete.
        
        TEACHING: This helps track vendor progress through the assessment.
        """
        total_questions = obj.template.questions.count()
        if total_questions == 0:
            return 0
        
        answered_questions = obj.responses.filter(
            answer_text__isnull=False
        ).exclude(answer_text='').count()
        
        return int((answered_questions / total_questions) * 100)
    
    def get_is_overdue(self, obj):
        """Check if assessment is past due date"""
        return obj.due_date < timezone.now().date() and obj.status != 'submitted'
    
    def get_days_until_due(self, obj):
        """Calculate days until due date"""
        days = (obj.due_date - timezone.now().date()).days
        return max(0, days)  # Don't show negative days


class AssessmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new assessments (assigning to vendors).
    
    TEACHING: When you create an assessment, you're essentially
    giving a vendor homework with a due date!
    """
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Assessment
        fields = [
            'id',  # Add ID so it's returned after creation
            'template',
            'vendor',
            'due_date',
            'vendor_notes',
            'template_name',  # Read-only field for display
            'status',  # Read-only field for display
        ]
    
    def validate_due_date(self, value):
        """Ensure due date is in the future"""
        if value <= timezone.now().date():
            raise serializers.ValidationError(
                "Due date must be in the future"
            )
        return value
    
    def create(self, validated_data):
        """
        Create assessment and auto-create response placeholders.
        
        TEACHING: When we assign an assessment, we create empty
        response records for each question. This makes it easier
        for vendors to track what they need to answer.
        """
        user = self.context['request'].user
        validated_data['assigned_by'] = user
        
        # Create the assessment
        assessment = super().create(validated_data)
        
        # Create empty responses for each question
        for question in assessment.template.questions.all():
            AssessmentResponse.objects.create(
                assessment=assessment,
                question=question
            )
        
        return assessment


class AssessmentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing assessments.
    """
    
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Assessment
        fields = [
            'id',
            'vendor_name',
            'template_name',
            'status',
            'due_date',
            'score',
            'passed',
            'completion_percentage',
            'is_overdue',
        ]
    
    def get_completion_percentage(self, obj):
        """Quick calculation for list view"""
        total = obj.template.questions.count()
        if total == 0:
            return 0
        answered = obj.responses.exclude(answer_text='').count()
        return int((answered / total) * 100)
    
    def get_is_overdue(self, obj):
        """Check overdue status"""
        return obj.due_date < timezone.now().date() and obj.status not in ['submitted', 'approved']