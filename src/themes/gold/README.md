# Gold Theme for Janeway

## Purpose
Gold is a custom Janeway journal theme.

Frontend development and Django backend integration
are handled separately.

## Source Directory
src/themes/gold/

## Directory Structure
- assets/css/ : CSS files
- assets/js/ : JavaScript files
- assets/fonts/ : Optional font files
- imgs/ : Theme images and fallback assets
- templates/core/ : Base layout, navigation and footer
- templates/journal/ : Journal pages
- templates/journal/homepage_elements/ : Homepage section templates
- templates/elements/ : Reusable Janeway components

## Frontend Development
Frontend developers should work inside the Gold theme.

Keep Janeway template tags, URL references,
context variables and template inheritance intact.

CSS components may be separated by section.
Import required stylesheets through assets/css/base.css.

Place new frontend assets in assets/ or imgs/.
Do not edit generated files inside src/static/gold/.

## Backend Integration
Homepage Elements require registration and integration
with the Janeway backend.

The presence of an HTML template alone does not
make a section editable through Homepage Elements.

Header, footer and hero are intended to remain
outside the editable homepage section workflow.

## Build
Run from the src directory:

python manage.py shell -c "from themes.gold.build_assets import build; build()"

The builder copies theme assets into src/static/gold/.

For production deployment, run the project's
standard collectstatic process after building.

## Deployment Checklist
1. Deploy the compatible Janeway codebase.
2. Ensure themes/gold/ is present.
3. Verify Django settings and installed dependencies.
4. Apply required database migrations, if any.
5. Build Gold assets.
6. Run collectstatic using production settings.
7. Configure and activate Gold for the intended journal.
8. Verify homepage, article pages, static assets and logs.

## Important Notes
- Do not deploy temporary CSS experiments or backup files.
- Do not commit Python cache files.
- Do not commit environment secrets.
- Uploaded journal media must remain separate from theme assets.
- Verify CDN dependencies and static file serving in production.
- Test on the target Janeway version before activation.

## Gold Backend Dependencies

Gold uses existing Janeway backend functionality:

- Journal homepage statistics: journal/views.py
- Editor-in-Chief information: journal/views.py
- Featured Articles: core/homepage_elements/featured/
- Abstract Indexing: plugins/abstract_indexing/

The Abstract Indexing plugin is not included inside the Gold theme.

Before using Abstract Indexing on the target server:

1. Ensure plugins/abstract_indexing/ exists.
2. Check migrations:
   python manage.py showmigrations abstract_indexing
3. Apply migrations if required:
   python manage.py migrate abstract_indexing
4. Install or update the plugin:
   python manage.py install_plugins abstract_indexing
5. Enable the Abstract Indexing Homepage Element through
   the journal administration interface when needed.

Do not enable Homepage Elements automatically during deployment.

## Deployment Scope

Installing Gold must not automatically:

- Change existing journal themes.
- Activate Homepage Elements.
- Modify journal records.
- Apply legacy Uncertainty patches.
- Replace existing frontend or backend files.

Theme activation and journal configuration are separate
administrative steps.
