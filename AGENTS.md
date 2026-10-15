<!-- ai-best-practices:start -->
<!-- Do not edit by hand inside the ai-best-practices markers in AGENTS.md; this block is regenerated when you update drupal/ai_best_practices. -->

## Drupal AI best practices

This project uses [`drupal/ai_best_practices`](https://www.drupal.org/project/ai_best_practices)
to provide AI guidance tailored for Drupal development.

**Skill discovery:** Skills are installed into `.agents/skills/` when you run
`composer install` or `composer update`. AI clients that support the
[Agent Skills specification](https://agentskills.io/specification) load skills
automatically from that directory — no manual listing needed. For clients that
do not yet support automatic discovery, this file (`AGENTS.md`) acts as a
compatibility fallback; add explicit skill references here only if your tooling
requires it.

**What to commit:** Add `.agents/` and `AGENTS.md` to version control so all
team members and CI environments share the same AI context. Also commit
tool-specific files such as `CLAUDE.md` and `GEMINI.md` if your team uses those
clients.
<!-- ai-best-practices:end -->

# Agent guidance for this Drupal site

This codebase is a Composer-managed Drupal site for Contract (Eastercon 2028, eastercon2028.org). Local development uses `ddev`. Working notes on the theme work are in `theme.md`.

## Repository layout

There are two separate git repositories.

- **Composer project** (this directory: `/var/www/html` in DDEV, `/var/www/drupal/drupal_eastercon2028` on live): `composer.json`, `composer.lock`, Drupal core and contributed projects, `.ddev/`, `.agents/`, and this file.
- **Site project** (`eastercon2028.org/eastercon2028_drupal/`, ignored by this repository; `/var/www/vhosts/eastercon2028.org/eastercon2028_drupal` on live): everything specific to this site.

```
eastercon2028.org/
  eastercon2028_drupal/            site project (own git repo)
    site/                          reached as web/sites/default (a symlink); on live as sites/eastercon2028.org
      settings.php, services.yml   no secrets; settings.php includes the secrets file below
      modules/                     site modules: heading_splitter (Contract's heading splits), contract_content (content export/import)
      themes/                      site theme: contract
      files/                       uploads and generated files (not in git)
    config/sync/                   configuration export, outside the webroot
    recipes/contract_content/      site content as default content (pages, guests, Canvas pages, menus, redirects, their media)
  eastercon2028_keys/              Key module files (Stripe, SMTP); outside both repositories
  eastercon2028_secrets/           settings.secret.php: database connection, hash salt, secret overrides; outside both repositories, empty on DDEV
```

`drupal/registration_theme` (maintained by this site's developer on drupal.org) comes from a Composer `path` repository: its git checkout is `modules/registration_theme` (branch `1.0.x`), symlinked to `web/themes/contrib/registration_theme`. Edit and commit it there; changes reach drupal.org by pushing that repository.

`drupal/registration_canvas_theme` (a sub-theme of `registration_theme`, being prepared as a drupal.org project) is set up the same way: `modules/registration_canvas_theme`, symlinked to `web/themes/contrib/registration_canvas_theme`. It is not yet a git repository or published. It has no module dependencies: its heading component and page title print text through `heading-text.html.twig` (first word as the highlighted start), which `contract` overrides to use the `heading_lead` filter from the site module `heading_splitter`.

`web/sites/default` is a symlink into the site project, so Drupal sees the site directory as `sites/default`. `config/sync` sits beside `site/`, not inside it, so it is never reachable through the webroot. `settings.php` points at it with `__DIR__ . '/../config/sync'`.

## Local environment (DDEV)

Run commands from the project root:

- Start or restart the local environment with `ddev start`, `ddev restart`, and `ddev stop`.
- Install PHP dependencies with `ddev composer install`.
- Open the site with `ddev launch`.
- Run Drush commands with `ddev drush <command>` such as `status`, `user:login`,  `cache:rebuild`, and `update:db`.

DDEV project config lives in `.ddev/config.yaml`. Use `.ddev/config.local.yaml` for machine-specific overrides.

An agent running inside the DDEV web container cannot run `ddev`; use `vendor/bin/drush <command>` from the project root instead. After moving or renaming a module or theme directory, or adding a service, the web process can keep serving stale class paths and return 500 ("Class ... not found") even though `drush cr` succeeds: also truncate the `cache_container` table and clear APCu/OPcache (restart PHP-FPM).

## Common Drupal workflows

- Add a module with `ddev composer require drupal/<project>`, then  `ddev drush pm:enable --yes <module_machine_name>`, then `ddev drush cache:rebuild`.
- Apply database updates after code changes with `ddev drush update:db --yes`.
- Import repository configuration into the site with `ddev drush config:import --yes`.
- Export site configuration back to the repo with `ddev drush config:export --yes`.
- Export content to the `contract_content` recipe with `ddev drush contract-content:export`, and import it (creating new items and overwriting existing ones by UUID) with `drush contract-content:import`. Core's `drush recipe` would skip existing content. Users, sent emails, newsletter issues and subscribers, and ConReg data are not exported: live is their source of truth.

## Guardrails

- Do not commit secrets or machine-local overrides such as `.env`, `settings.local.php`, `settings.ddev.php`, or `.ddev/config.local.yaml`. Secrets go in `eastercon2028.org/eastercon2028_secrets/settings.secret.php`, which `settings.php` includes last; `site/settings.secret.example.php` shows what belongs in it.
- Do not commit `vendor/`, uploaded files under `site/files`, the Key module files in `eastercon2028_keys`, the `eastercon2028_secrets` directory, `.ddev/claude-code/` (it holds credentials), or database dumps (`live/`).
- Do not edit Drupal core or contributed projects in place.
- Put custom code in the site project: `eastercon2028.org/eastercon2028_drupal/site/modules` and `.../site/themes` (Drupal finds them as `sites/default/modules` and `sites/default/themes`). Do not create `web/modules/custom` or `web/themes/custom`.
- Export configuration to `eastercon2028.org/eastercon2028_drupal/config/sync` (this is the configured sync directory). Keep secrets out of it: `friendlycaptcha.settings` holds an `api_key` in plain text, which should be overridden in the secrets file (`settings.secret.php`) instead of exported. The Key module entries only reference key files, so they are safe.
- The Bitwise font (`site/themes/contract/fonts/bitwise/`) is served with its designer's written permission; keep its `!license.txt` beside it.

## References

- https://docs.ddev.com/en/stable/
- https://www.drupal.org/docs/administering-a-drupal-site/configuration-management/workflow-using-drush
