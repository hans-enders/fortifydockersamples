import jenkins.model.*
import hudson.model.*
import hudson.tools.*
import hudson.plugins.gradle.*

def instance = Jenkins.getInstance()
def gradle = new GradleInstallation("Gradle 4.3.0", "", [new InstallSourceProperty([new GradleInstaller("4.3.0")])])
def descriptor = instance.getDescriptorByType(GradleInstallation.DescriptorImpl)
descriptor.setInstallations(gradle)
descriptor.save()
