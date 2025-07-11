from typing import TypedDict
from Mir import LanguageServer, deno, LoaderInStatusBar, PackageStorage, command
import sublime


server_storage = PackageStorage(tag='0.0.1')
server_path = server_storage / "language-server" / 'node_modules' / 'typescript-language-server' / 'lib' / 'cli.mjs'

async def package_storage_setup():
    if server_path.exists():
        return
    await deno.setup()
    server_storage.copy("./language-server")
    with LoaderInStatusBar(f'installing typescript-language-server'):
        await command([deno.path, "install"], cwd=str(server_storage / "language-server"))


class TypeScriptLanguageServer(LanguageServer):
    name='typescript-language-server'
    activation_events={
        'selector': 'source.js, source.jsx, source.ts, source.tsx',
    }
    settings_file="Mir-typescript.sublime-settings"

    async def activate(self):
        # setup runtime and install dependencies
        await package_storage_setup()

        self.on_request('custom_request', custom_request_handler)
        self.on_notification('$/typescriptVersion', on_typescript_version)
        await self.initialize({
            'communication_channel': 'stdio',
            'command': [deno.path, 'run', '-A', server_path, '--stdio'],
            'initialization_options': self.settings.get('typescript-language-server.initialization_options')
        })


class SomeExample(TypedDict):
    name: str
    age: int

def custom_request_handler(params: SomeExample):
    print(params['name'])

class TypescriptVersionParams(TypedDict):
    source: str
    version: str

def on_typescript_version(params: TypescriptVersionParams):
    sublime.status_message(params['source'] + f"({params['version']})")

