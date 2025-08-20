from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    organizers = models.ManyToManyField(
        "auth.User", related_name="organizations", blank=True, null=True, db_index=True
    )

    def __str__(self):
        return self.name
