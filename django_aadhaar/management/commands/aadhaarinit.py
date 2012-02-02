from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import resolve 
import sys, os
from distutils import dir_util, file_util

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        )

    help = 'Install Aadhaar fixtures'
    
    def findpath(self, path):
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.abspath(os.path.join(parent_dir,path))

    def handle(self, **options):
        working_directory = os.getcwd() 
        module_path = self.findpath("..") 
        dir_util.copy_tree(module_path + "/fixtures", 
                           working_directory + "/fixtures", update=1)
        print "Installed configuration files required for aadhaar authentication" 
