import quart

import models

class Core(quart.Blueprint):
    def __init__(self, app: models.App) -> None:
        super().__init__('core', __name__, template_folder = '../templates/core')
        self.app = app

        @self.route('/')
        async def landing():
            return await quart.render_template('landing.html')

        @self.route('/oauth2')
        async def oauth2():
            return quart.redirect('https://discord.com/api/oauth2/authorize?client_id=895053517243433060&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Foauth2%2Fredirect&response_type=code&scope=identify%20guilds')

        @self.route('/oauth2/redirect')
        async def oauth2_redirect():
            quart.session['access_token'], quart.session['refresh_token'] = await app.rest.authorize_tokens(quart.request.args['code'])
            return quart.redirect('/guilds')

        @self.route('/guilds')
        async def guilds():
            guilds, invite = await app.rest.fetch_my_guilds(quart.session['access_token'])
            return await quart.render_template('guilds.html', guilds = guilds, invite = invite)

def register(app: models.App) -> None:
    app.register_blueprint(Core(app))
