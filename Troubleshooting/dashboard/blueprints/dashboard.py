import quart

import models

class Dashboard(quart.Blueprint):
    def __init__(self, app: models.App) -> None:
        super().__init__('dashboard', __name__, template_folder = '../templates/dashboard')
        self.app = app

        @self.route('/dashboard/<guild_id>', ['GET', 'POST'])
        async def dashboard(guild_id):
            if quart.request.method == 'POST':
                color: str = (await quart.request.form)['guild_color']
                await app.pool.execute('UPDATE guilds SET color = $1 WHERE guild_id = $2', int(color.removeprefix('#'), 16), int(guild_id))
            guild = await app.rest.fetch_guild(guild_id)
            return await quart.render_template('dashboard.html', guild = guild)

def register(app: models.App) -> None:
    app.register_blueprint(Dashboard(app))
