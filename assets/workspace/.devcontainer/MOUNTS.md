# Mounting Additional Folders

This devcontainer supports mounting additional folders/projects using Docker Compose override files.

## Quick Start

1. **Copy the example file:**

   ```bash
   cp .devcontainer/docker-compose.override.yml.example \
      .devcontainer/docker-compose.override.yml
   ```

2. **Edit the file and uncomment the mounts you need:**

```yaml
   version: '3.8'

   services:
     devcontainer:
       volumes:
         - ../other-project:/workspace/other-project:cached
         - ~/shared-libs:/workspace/shared:cached
   ```

1. **Rebuild the devcontainer:**
   - In VS Code: `Cmd/Ctrl+Shift+P` → "Dev Containers: Rebuild Container"
   - Or: `devcontainer up --remove-existing-container`

## How It Works

Docker Compose automatically merges files in this order:
1. `docker-compose.yml` (base configuration, committed to git)
2. `docker-compose.override.yml` (your local mounts, gitignored)

The override file is **gitignored**, so your personal mount configuration won't be committed or shared with others.

## Mount Patterns

### Sibling Projects
Mount a project from a sibling directory:

```yaml
volumes:
  - ../other-project:/workspace/other-project:cached
```

### Home Directory
Mount from your home directory:

```yaml
volumes:
  - ~/shared-resources:/workspace/shared:cached
```

### Absolute Path
Mount from an absolute path:

```yaml
volumes:
  - /path/to/project:/workspace/project-name:cached
```

### Read-Only Mount
Mount with read-only access:

```yaml
volumes:
  - ~/reference-docs:/workspace/docs:ro
```

### Multiple Mounts
Add as many mounts as you need:

```yaml
volumes:
  - ../backend-api:/workspace/backend-api:cached
  - ../frontend-app:/workspace/frontend-app:cached
  - ~/shared-libs:/workspace/libs:cached
  - ~/config:/workspace/config:ro
```

## Mount Options

- `:cached` - Optimizes performance for macOS/Windows (recommended for most mounts)
- `:ro` - Read-only mount
- `:rw` - Read-write mount (default if not specified)

## Accessing Mounted Folders

Mounted folders appear under `/workspace/`:

```bash
# List all workspace folders
ls -la /workspace/

# Access mounted project
cd /workspace/other-project
```

## Important Notes

1. **Paths are relative to `.devcontainer/` directory**
   - `..` refers to the project root
   - `../..` refers to the parent of the project root

2. **The override file is personal**
   - Each developer can have their own mounts
   - Changes won't affect other team members

3. **Rebuild required**
   - After changing mounts, rebuild the container
   - Running containers won't see new mounts

4. **Performance considerations**
   - Use `:cached` for better performance on macOS/Windows
   - Avoid mounting large directories unnecessarily
   - Consider read-only (`:ro`) for reference materials

## Troubleshooting

### Mount not showing up
- Ensure you rebuilt the container after adding the mount
- Check the path is correct relative to `.devcontainer/`
- Verify the source directory exists on your host

### Permission issues
- The container runs as root by default
- Host file permissions are preserved in the mount

### Performance issues
- Use `:cached` mount option
- Avoid mounting large node_modules or cache directories
- Consider using `.dockerignore` for build contexts

## Examples

### Multi-project monorepo development

```yaml
services:
  devcontainer:
    volumes:
      - ../api-gateway:/workspace/api-gateway:cached
      - ../user-service:/workspace/user-service:cached
      - ../shared-types:/workspace/shared-types:cached
```

### Frontend + Backend development

```yaml
services:
  devcontainer:
    volumes:
      - ../backend:/workspace/backend:cached
      - ../frontend:/workspace/frontend:cached
      - ~/shared-components:/workspace/components:cached
```

### Reference and configuration

```yaml
services:
  devcontainer:
    volumes:
      - ~/project-docs:/workspace/docs:ro
      - ~/shared-config:/workspace/config:ro
      - ~/.aws:/root/.aws:ro  # AWS credentials
```
