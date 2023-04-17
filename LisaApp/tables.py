import django_tables2 as tables
from .models import *
from django.utils import timezone
from django.urls import reverse

class VideoTable(tables.Table):
    class Meta:
        model = Video
        template_name = 'django_tables2/bootstrap.html'
        fields = ('id','video_link', 'name', 'description')

class ProgramTable(tables.Table):
    id = tables.LinkColumn('program_detail', args=[tables.A('pk')])
    name = tables.Column()
    description = tables.Column()

    class Meta:
        model = Program
        template_name = 'django_tables2/bootstrap.html'
        fields = ('id', 'name', 'description')

class UserTable(tables.Table):
    class Meta:
        model = User
        template_name = 'django_tables2/bootstrap.html'
        fields = ('id','username', 'first_name', 'last_name', 'email')

class UPJunctionTable(tables.Table):
    program = tables.Column(accessor='program.name')
    class Meta:
        model = UPJunction
        fields = ('program', 'start_date' , 'completed', 'completion_date')
        template_name = "django_tables2/bootstrap-responsive.html"
