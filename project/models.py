from djongo import models

class Project(models.Model):
    user_cognito_id = models.CharField(max_length=255)  # Reference cognitoUserId
    _id = models.ObjectIdField(primary_key=True)
    project_name = models.CharField(max_length=100, null=False)
    project_description = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'project'
        verbose_name_plural = 'projects'
        db_table = "projects"

