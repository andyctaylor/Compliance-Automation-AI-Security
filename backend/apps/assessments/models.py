from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization
from apps.vendors.models import Vendor

User = get_user_model()


class AssessmentTemplate(models.Model):
    """
    A reusable template for assessments.
    
    TEACHING MOMENT: Templates let you create once, use many times.
    Like a master copy of a test that different students (vendors) can take.
    """
    
    # Which organization owns this template
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='assessment_templates',
        help_text="Organization that created this template"
    )
    
    # Template details
    name = models.CharField(
        max_length=255,
        help_text="Template name (e.g., 'HIPAA Security Assessment')"
    )
    
    description = models.TextField(
        help_text="What this assessment covers"
    )
    
    # Assessment type
    ASSESSMENT_TYPE_CHOICES = [
        ('hipaa_security', 'HIPAA Security Rule'),
        ('hipaa_privacy', 'HIPAA Privacy Rule'), 
        ('general_security', 'General Security'),
        ('soc2', 'SOC 2 Compliance'),
        ('vendor_risk', 'Vendor Risk Assessment'),
        ('custom', 'Custom Assessment'),
    ]
    
    assessment_type = models.CharField(
        max_length=50,
        choices=ASSESSMENT_TYPE_CHOICES,
        default='vendor_risk',
        help_text="Type of compliance assessment"
    )
    
    # Scoring
    total_points = models.IntegerField(
        default=100,
        help_text="Maximum possible score"
    )
    
    passing_score = models.IntegerField(
        default=70,
        help_text="Minimum score to pass"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Is this template currently in use?"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_templates'
    )
    
    class Meta:
        ordering = ['name']
        unique_together = ['organization', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class Question(models.Model):
    """
    Individual questions within an assessment template.
    
    TEACHING: Questions can be different types - yes/no, multiple choice, text, etc.
    Each question can have different point values based on importance.
    """
    
    template = models.ForeignKey(
        AssessmentTemplate,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    # Question content
    question_text = models.TextField(
        help_text="The actual question to ask"
    )
    
    # Help text for vendors
    help_text = models.TextField(
        blank=True,
        help_text="Additional guidance for answering this question"
    )
    
    # Question types
    QUESTION_TYPE_CHOICES = [
        ('yes_no', 'Yes/No'),
        ('multiple_choice', 'Multiple Choice'),
        ('text', 'Text Response'),
        ('number', 'Numeric Response'),
        ('date', 'Date Response'),
        ('file', 'File Upload Required'),
    ]
    
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='yes_no'
    )
    
    # For multiple choice questions
    choices = models.JSONField(
        null=True,
        blank=True,
        help_text="Choices for multiple choice questions"
    )
    
    # Scoring
    points = models.IntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text="Points for correct/compliant answer"
    )
    
    # What constitutes a "passing" answer
    correct_answer = models.JSONField(
        null=True,
        blank=True,
        help_text="What answer gives full points (for auto-scoring)"
    )
    
    # Organization
    section = models.CharField(
        max_length=100,
        blank=True,
        help_text="Section/category of the question"
    )
    
    order = models.IntegerField(
        default=0,
        help_text="Order within the assessment"
    )
    
    # Requirements
    is_required = models.BooleanField(
        default=True,
        help_text="Must this question be answered?"
    )
    
    # Critical compliance flag
    is_critical = models.BooleanField(
        default=False,
        help_text="Is this a critical compliance question?"
    )
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class Assessment(models.Model):
    """
    An actual assessment instance sent to a vendor.
    
    TEACHING: This is like a test paper given to a specific student (vendor).
    It's based on a template but tracks this vendor's specific responses.
    """
    
    # Links
    template = models.ForeignKey(
        AssessmentTemplate,
        on_delete=models.PROTECT,  # Can't delete template if assessments exist
        related_name='assessments'
    )
    
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    
    # Assignment details
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_assessments'
    )
    
    assigned_date = models.DateTimeField(auto_now_add=True)
    
    due_date = models.DateField(
        help_text="When the vendor must complete this"
    )
    
    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending - Not Started'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted - Awaiting Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected - Needs Revision'),
        ('expired', 'Expired - Past Due'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Completion tracking
    started_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When vendor started the assessment"
    )
    
    submitted_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When vendor submitted responses"
    )
    
    reviewed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When assessment was reviewed"
    )
    
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_assessments'
    )
    
    # Scoring
    score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Final score as percentage"
    )
    
    passed = models.BooleanField(
        null=True,
        blank=True,
        help_text="Did they pass the assessment?"
    )
    
    # Feedback
    reviewer_notes = models.TextField(
        blank=True,
        help_text="Internal notes from reviewer"
    )
    
    vendor_notes = models.TextField(
        blank=True,
        help_text="Notes from vendor"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.vendor.name} - {self.template.name} ({self.status})"
    
    def calculate_score(self):
        """
        Calculate the assessment score based on responses.
        
        TEACHING: This method goes through all answers and tallies the score.
        Critical questions might have special handling.
        """
        total_points = 0
        earned_points = 0
        
        # IMPORTANT: Get fresh responses from database to avoid cached data
        # Using select_related to optimize the query
        fresh_responses = self.responses.select_related('question').all()
        
        for response in fresh_responses:
            if response.question.is_required or response.answer_text:
                total_points += response.question.points
                earned_points += response.points_earned
        
        if total_points > 0:
            self.score = int((earned_points / total_points) * 100)
            self.passed = self.score >= self.template.passing_score
        else:
            self.score = 0
            self.passed = False
        
        self.save()
        return self.score


class AssessmentResponse(models.Model):
    """
    A vendor's response to a specific question.
    
    TEACHING: Each answer is stored separately so we can track
    exactly what was answered, when, and score it individually.
    """
    
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # The actual answer (stored as JSON for flexibility)
    answer_text = models.TextField(
        blank=True,
        help_text="Text answer or JSON for complex answers"
    )
    
    answer_json = models.JSONField(
        null=True,
        blank=True,
        help_text="Structured answer data"
    )
    
    # File uploads for document requests
    # Note: In production, you'd store file path or S3 URL
    answer_file = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to uploaded file"
    )
    
    # Scoring
    points_earned = models.IntegerField(
        default=0,
        help_text="Points earned for this answer"
    )
    
    # Review status
    is_approved = models.BooleanField(
        null=True,
        blank=True,
        help_text="Has reviewer approved this answer?"
    )
    
    reviewer_comment = models.TextField(
        blank=True,
        help_text="Reviewer's comment on this answer"
    )
    
    # Timestamps
    answered_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['assessment', 'question']
        ordering = ['question__order']
    
    def __str__(self):
        return f"{self.assessment.vendor.name} - Q{self.question.order}"
    
    def auto_score(self):
        """
        Automatically score the response if possible.
        
        TEACHING: Some questions can be auto-scored (like yes/no),
        while others need human review (like text explanations).
        """
        if self.question.question_type == 'yes_no':
            # For yes/no, check if answer matches correct answer
            if self.answer_text == self.question.correct_answer:
                self.points_earned = self.question.points
            else:
                self.points_earned = 0
        
        elif self.question.question_type == 'multiple_choice':
            # Check if selected choice is correct
            if self.answer_json and self.answer_json.get('selected') == self.question.correct_answer:
                self.points_earned = self.question.points
            else:
                self.points_earned = 0
        
        # Text and file responses need manual review
        # Number and date might have ranges to check
        
        self.save()
        return self.points_earned