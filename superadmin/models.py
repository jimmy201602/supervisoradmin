from django.db import models
from django.utils.translation import ugettext_lazy as _

class NodeEnv(models.Model):
    name = models.CharField(_('Name'),max_length=50,help_text=_('Node name'))
    host = models.GenericIPAddressField(_('Host IP'), protocol='ipv4')
    port = models.PositiveIntegerField(_('Port'),help_text=_('Supervisor remote manage port'))    
    username = models.CharField(_('Username'),max_length=50,help_text=_('Supervisor login user name'))
    password = models.CharField(_('Password'),max_length=50,help_text=_('Supervior login password'))

    def __unicode__(self):
        return self.name

class EnvironmentGroups(models.Model):
    name = models.CharField(_('Name'),max_length=50,help_text=_('Environment name'))
    members = models.ManyToManyField(NodeEnv,help_text=_('Environment members'))

    def __unicode__(self):
        return  self.name

class Log(models.Model):
    module_name = models.CharField(_('Module name'),max_length=50,help_text=_('Log module name'))
    level = models.CharField(_('level'),max_length=50,help_text=_('Log level'))
    message = models.TextField(_('Message'),max_length=2000,help_text=_('Log detail message'))
    create_datetime = models.DateTimeField(_('Create datetime'),auto_now_add=True,help_text=_('Created datetime'))