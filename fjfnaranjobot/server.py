from warnings import filterwarnings

import bjoern

from fjfnaranjobot.wsgi import application

filterwarnings("ignore", ".*per_message=False.*CallbackQueryHandler.*", UserWarning)

bjoern.listen(application, "0.0.0.0", 8001)
bjoern.run()
