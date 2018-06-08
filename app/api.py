from app import app
from flask.ext.restful import Api

from resources.jobs.jobs import Job_queue, FilesResource, \
    DownloadFilesResource, CopyChewSchema, SetNGSOntoOutput, FlowcraftInspect
from resources.downloads.downloads import DownloadResults

# Setup API
api = Api(app)

api.add_resource(Job_queue, '/jobs/')

# trigger flocraft inspect
api.add_resource(FlowcraftInspect, '/jobs/inspect')

# get files from user
api.add_resource(FilesResource, '/jobs/fastqs/')

# set parameters of NGSOnto
api.add_resource(SetNGSOntoOutput, '/jobs/setoutput/')

# download files to user area
api.add_resource(DownloadFilesResource, '/jobs/download/')

# download files to user area
api.add_resource(DownloadResults, '/jobs/results/download/')

# get files from user
api.add_resource(CopyChewSchema, '/jobs/schema/copy/')
