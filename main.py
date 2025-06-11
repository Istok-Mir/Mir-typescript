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
        await self.connect('stdio', {
            'cmd': [deno.path, 'run', '-A', server_path, '--stdio'],
            'initialization_options': {'completionDisableFilterText': True, 'disableAutomaticTypingAcquisition': False, 'locale': 'en', 'maxTsServerMemory': 0, 'npmLocation': '', 'plugins': [], 'preferences': {'allowIncompleteCompletions': True, 'allowRenameOfImportPath': True, 'allowTextChangesInNewFiles': True, 'autoImportFileExcludePatterns': [], 'disableSuggestions': False, 'displayPartsForJSDoc': True, 'excludeLibrarySymbolsInNavTo': True, 'generateReturnInDocTemplate': True, 'importModuleSpecifierEnding': 'auto', 'importModuleSpecifierPreference': 'shortest', 'includeAutomaticOptionalChainCompletions': True, 'includeCompletionsForImportStatements': True, 'includeCompletionsForModuleExports': True, 'includeCompletionsWithClassMemberSnippets': True, 'includeCompletionsWithInsertText': True, 'includeCompletionsWithObjectLiteralMethodSnippets': True, 'includeCompletionsWithSnippetText': True, 'includePackageJsonAutoImports': 'auto', 'interactiveInlayHints': True, 'jsxAttributeCompletionStyle': 'auto', 'lazyConfiguredProjectsFromExternalProject': False, 'organizeImportsAccentCollation': True, 'organizeImportsCaseFirst': False, 'organizeImportsCollation': 'ordinal', 'organizeImportsCollationLocale': 'en', 'organizeImportsIgnoreCase': 'auto', 'organizeImportsNumericCollation': False, 'providePrefixAndSuffixTextForRename': True, 'provideRefactorNotApplicableReason': True, 'quotePreference': 'auto', 'useLabelDetailsInCompletionEntries': True}, 'tsserver': {'fallbackPath': '', 'logDirectory': '', 'logVerbosity': 'off', 'path': '', 'trace': 'off', 'useSyntaxServer': 'auto'}}
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

