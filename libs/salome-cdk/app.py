import aws_cdk as cdk

from stacks.app import SalomeAppStack

app = cdk.App()

SalomeAppStack(app, "salome-app")

app.synth()
