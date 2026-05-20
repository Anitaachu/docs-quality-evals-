

# Ruby

> Test supports deploying any Ruby application. Your application can use any Ruby application server such as Puma or Unicorn and deploying a Rails or a Sinatra app is very straight forward.


export const DynamicCodeBlock = ({language = 'yaml', filename, icon, lines, wrap, expandable, highlight, focus, children}) => {
  const STORAGE_KEY = 'upsun_versions_cache';
  const COMPOSABLE_STORAGE_KEY = 'upsun_composable_cache';
  const CACHE_TTL = 5 * 60 * 1000;
  const API_URL = 'https://meta.upsun.com/images';
  const COMPOSABLE_API_URL = 'https://meta.upsun.com/composable';
  const DEBUG_PREFIX = '[DynamicCodeBlock cache]';
  const [versionData, setVersionData] = useState(null);
  const [versionError, setVersionError] = useState(false);
  const [composableData, setComposableData] = useState(null);
  const [composableError, setComposableError] = useState(false);
  useEffect(() => {
    const fetchData = async () => {
      let cachedData = null;
      let cachedEtag = null;
      if (typeof localStorage !== 'undefined') {
        try {
          const cached = localStorage.getItem(STORAGE_KEY);
          if (cached) {
            const parsed = JSON.parse(cached);
            cachedData = parsed?.data || null;
            cachedEtag = parsed?.etag || null;
            if (cachedData && Date.now() - parsed.timestamp < CACHE_TTL) {
              return cachedData;
            }
          }
        } catch (err) {
          console.error('Failed to load from cache:', err);
        }
      }
      const requestHeaders = cachedEtag ? {
        'If-None-Match': cachedEtag
      } : {};
      console.debug(`${DEBUG_PREFIX} revalidating`, {
        storageKey: STORAGE_KEY,
        hasCachedData: Boolean(cachedData),
        hasCachedEtag: Boolean(cachedEtag)
      });
      const response = await fetch(API_URL, {
        headers: requestHeaders
      });
      if (response.status === 304 && cachedData) {
        console.debug(`${DEBUG_PREFIX} revalidated (304)`, {
          storageKey: STORAGE_KEY
        });
        if (typeof localStorage !== 'undefined') {
          try {
            const etag = response.headers.get('etag') || cachedEtag;
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
              data: cachedData,
              etag,
              timestamp: Date.now()
            }));
          } catch (err) {
            console.error('Failed to refresh cache metadata:', err);
          }
        }
        return cachedData;
      }
      if (!response.ok) throw new Error(`API request failed: ${response.statusText}`);
      const data = await response.json();
      const etag = response.headers.get('etag');
      console.debug(`${DEBUG_PREFIX} refreshed (200)`, {
        storageKey: STORAGE_KEY,
        etag
      });
      if (typeof localStorage !== 'undefined') {
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify({
            data,
            etag,
            timestamp: Date.now()
          }));
        } catch (err) {
          console.error('Failed to cache data:', err);
        }
      }
      return data;
    };
    fetchData().then(data => setVersionData(data)).catch(err => console.error('Failed to fetch version data:', err));
  }, []);
  const findHighestVersion = versionsMap => {
    if (!versionsMap || Object.keys(versionsMap).length === 0) return null;
    const entries = Object.entries(versionsMap);
    const active = entries.filter(([, v]) => v.upsun && v.upsun.status === 'supported' || v.upsun && v.upsun.status === 'deprecated');
    const candidates = active.length > 0 ? active : entries;
    let [highestName] = candidates[0];
    for (let i = 1; i < candidates.length; i++) {
      const [currentName] = candidates[i];
      const cp = currentName.split('.').map(Number);
      const hp = highestName.split('.').map(Number);
      for (let j = 0; j < Math.max(cp.length, hp.length); j++) {
        if ((cp[j] || 0) > (hp[j] || 0)) {
          highestName = currentName;
          break;
        } else if ((cp[j] || 0) < (hp[j] || 0)) {
          break;
        }
      }
    }
    return highestName;
  };
  const getVersion = (lang, requestedVersion = 'latest') => {
    if (lang === 'composable') {
      if (!composableData || !composableData.versions || Object.keys(composableData.versions).length === 0) return null;
      if (requestedVersion && requestedVersion !== 'latest') {
        return (requestedVersion in composableData.versions) ? requestedVersion : null;
      }
      return findHighestVersion(composableData.versions);
    }
    if (!versionData) return null;
    const imageData = versionData[lang];
    if (!imageData || !imageData.versions || Object.keys(imageData.versions).length === 0) {
      return null;
    }
    if (requestedVersion && requestedVersion !== 'latest') {
      return (requestedVersion in imageData.versions) ? requestedVersion : null;
    }
    return findHighestVersion(imageData.versions);
  };
  let code = typeof children === 'string' ? children : String(children || '');
  const codeLines = code.split('\n');
  while (codeLines.length > 0 && codeLines[0].trim() === '') codeLines.shift();
  while (codeLines.length > 0 && codeLines[codeLines.length - 1].trim() === '') codeLines.pop();
  if (codeLines.length > 0) {
    const indents = codeLines.filter(line => line.trim().length > 0).map(line => line.match(/^[ \t]*/)[0].length);
    const minIndent = Math.min(...indents);
    code = codeLines.map(line => line.slice(minIndent)).join('\n');
  }
  code = code.replace(/\{\{version:(.*?)\}\}/g, (match, params) => {
    const parts = params.split(':');
    const lang = parts[0];
    const ver = parts[1] || 'latest';
    const isComposable = lang === 'composable';
    const hasError = isComposable ? composableError : versionError;
    const dataReady = isComposable ? composableData !== null : versionData !== null;
    if (hasError) return '(unavailable)';
    if (dataReady) {
      const resolvedVersion = getVersion(lang, ver);
      return resolvedVersion || match;
    }
    return '...';
  });
  const codeBlockProps = {
    language,
    ...filename && ({
      filename
    }),
    ...icon && ({
      icon
    }),
    ...lines !== undefined && ({
      lines
    }),
    ...wrap !== undefined && ({
      wrap
    }),
    ...expandable !== undefined && ({
      expandable
    }),
    ...highlight && ({
      highlight
    }),
    ...focus && ({
      focus
    })
  };
  return <CodeBlock {...codeBlockProps}>{code}</CodeBlock>;
};

export const RepoList = ({lang, displayName}) => <Info>
    To deploy a {displayName} project, create a new project from the{' '}
    <a href="https://console.upsun.com/projects/create-project">Upsun Console</a>{' '}
    and select a template, or push your existing code.
  </Info>;

export const VersionDeprecatedBlock = () => <>
    <h3 id="deprecated-versions">Deprecated versions</h3>
    <p>
    The following versions are <a href="/docs/glossary#deprecated-versions">deprecated</a>.
    They're available, but they don't receive security updates from upstream and aren't guaranteed to work.
    They'll be removed in the future – consider migrating to a <a href="#supported-versions">supported version</a>.
    </p>
  </>;

export const MetaImageVersionList = ({language, status}) => {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const STORAGE_KEY = 'upsun_versions_cache';
  const CACHE_TTL = 5 * 60 * 1000;
  const API_URL = 'https://meta.upsun.com/images';
  useEffect(() => {
    if (!language) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    const fetchData = async () => {
      let cachedData = null;
      let cachedEtag = null;
      if (typeof localStorage !== 'undefined') {
        try {
          const cached = localStorage.getItem(STORAGE_KEY);
          if (cached) {
            const parsed = JSON.parse(cached);
            cachedData = parsed?.data || null;
            cachedEtag = parsed?.etag || null;
            if (cachedData && Date.now() - parsed.timestamp < CACHE_TTL) return cachedData;
          }
        } catch (error_) {
          console.error('Failed to load from cache:', error_);
        }
      }
      const requestHeaders = cachedEtag ? {
        'If-None-Match': cachedEtag
      } : {};
      const response = await fetch(API_URL, {
        headers: requestHeaders
      });
      if (response.status === 304 && cachedData) {
        if (typeof localStorage !== 'undefined') {
          try {
            const etag = response.headers.get('etag') || cachedEtag;
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
              data: cachedData,
              etag,
              timestamp: Date.now()
            }));
          } catch (error_) {
            console.error('Failed to refresh cache metadata:', error_);
          }
        }
        return cachedData;
      }
      if (!response.ok) throw new Error(`API request failed: ${response.statusText}`);
      const data = await response.json();
      const etag = response.headers.get('etag');
      if (typeof localStorage !== 'undefined') {
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify({
            data,
            etag,
            timestamp: Date.now()
          }));
        } catch (error_) {
          console.error('Failed to cache data:', error_);
        }
      }
      return data;
    };
    fetchData().then(data => {
      if (!data || !data[language]) {
        setVersions([]);
        setLoading(false);
        return;
      }
      const imageData = data[language];
      if (!imageData.versions) {
        setVersions([]);
        setLoading(false);
        return;
      }
      let versionList = Object.entries(imageData.versions).map(([name, v]) => ({
        name,
        status: v.upsun?.status || v.status
      })).sort((a, b) => {
        const aParts = a.name.split('.').map(Number);
        const bParts = b.name.split('.').map(Number);
        const max = Math.max(aParts.length, bParts.length);
        for (let i = 0; i < max; i++) {
          const av = aParts[i] || 0;
          const bv = bParts[i] || 0;
          if (av !== bv) return bv - av;
        }
        return 0;
      });
      if (status) {
        versionList = versionList.filter(v => v.status === status);
      }
      setVersions(versionList);
      setLoading(false);
    }).catch(error_ => {
      console.error('MetaImageVersionList error:', error_);
      setError(error_.message);
      setLoading(false);
    });
  }, [language, status]);
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!versions || versions.length === 0) {
    if (status === 'incoming') return null;
    return <p>No versions available! Contact support.</p>;
  }
  let incomingBlock = null;
  if (status === 'incoming' && versions.length > 0) {
    incomingBlock = `These versions are not yet available but are expected to be released soon.`;
  }
  return incomingBlock ? <Note>
      <p>{incomingBlock}</p>
      <ul>
        {versions.map(version => <li className="image-version" key={version.name}>
            {version.name} {version.status === 'beta' && <span className="badge">Beta</span>}
          </li>)}
      </ul>
    </Note> : <ul>
      {versions.map(version => <li className="image-version" key={version.name}>
          {version.name} {version.status === 'beta' && <span className="badge">Beta</span>}
        </li>)}
    </ul>;
};

export const MetaImageVersion = ({language, version}) => {
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const isComposable = language === 'composable';
  const STORAGE_KEY = isComposable ? 'upsun_composable_cache' : 'upsun_versions_cache';
  const CACHE_TTL = 5 * 60 * 1000;
  const API_URL = isComposable ? 'https://meta.upsun.com/composable' : 'https://meta.upsun.com/images';
  const findHighestVersion = versionsMap => {
    if (!versionsMap || Object.keys(versionsMap).length === 0) return null;
    const entries = Object.entries(versionsMap);
    const active = entries.filter(([, v]) => v.upsun && v.upsun.status === 'supported' || v.upsun && v.upsun.status === 'deprecated');
    const candidates = active.length > 0 ? active : entries;
    let [highestName] = candidates[0];
    for (let i = 1; i < candidates.length; i++) {
      const [currentName] = candidates[i];
      const cp = currentName.split('.').map(Number);
      const hp = highestName.split('.').map(Number);
      for (let j = 0; j < Math.max(cp.length, hp.length); j++) {
        if ((cp[j] || 0) > (hp[j] || 0)) {
          highestName = currentName;
          break;
        } else if ((cp[j] || 0) < (hp[j] || 0)) {
          break;
        }
      }
    }
    return highestName;
  };
  useEffect(() => {
    if (!language) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    const fetchData = async () => {
      let cachedData = null;
      let cachedEtag = null;
      if (typeof localStorage !== 'undefined') {
        try {
          const cached = localStorage.getItem(STORAGE_KEY);
          if (cached) {
            const parsed = JSON.parse(cached);
            cachedData = parsed?.data || null;
            cachedEtag = parsed?.etag || null;
            if (cachedData && Date.now() - parsed.timestamp < CACHE_TTL) return cachedData;
          }
        } catch (error_) {
          console.error('Failed to load from cache:', error_);
        }
      }
      const requestHeaders = cachedEtag ? {
        'If-None-Match': cachedEtag
      } : {};
      const response = await fetch(API_URL, {
        headers: requestHeaders
      });
      if (response.status === 304 && cachedData) {
        if (typeof localStorage !== 'undefined') {
          try {
            const etag = response.headers.get('etag') || cachedEtag;
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
              data: cachedData,
              etag,
              timestamp: Date.now()
            }));
          } catch (error_) {
            console.error('Failed to refresh cache metadata:', error_);
          }
        }
        return cachedData;
      }
      if (!response.ok) throw new Error(`API request failed: ${response.statusText}`);
      const data = await response.json();
      const etag = response.headers.get('etag');
      if (typeof localStorage !== 'undefined') {
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify({
            data,
            etag,
            timestamp: Date.now()
          }));
        } catch (error_) {
          console.error('Failed to cache data:', error_);
        }
      }
      return data;
    };
    fetchData().then(data => {
      if (!data) {
        setSelectedVersion(null);
        setLoading(false);
        return;
      }
      const imageData = isComposable ? data : data[language];
      if (!imageData || !imageData.versions || Object.keys(imageData.versions).length === 0) {
        setSelectedVersion(null);
        setLoading(false);
        return;
      }
      let versionName = null;
      if (version && version !== 'latest') {
        versionName = (version in imageData.versions) ? version : null;
      } else {
        versionName = findHighestVersion(imageData.versions);
      }
      setSelectedVersion(versionName);
      setLoading(false);
    }).catch(error_ => {
      console.error('MetaImageVersion error:', error_);
      setError(error_.message);
      setLoading(false);
    });
  }, [language, version]);
  if (loading) return <span>…</span>;
  if (error) return <span title={error}>⚠ unavailable</span>;
  if (!selectedVersion) return <span>No version found</span>;
  return <span>{selectedVersion}</span>;
};

export const DisclaimerNix = () => <Tip>
    You can now use composable image to install runtimes and tools in your application container. To find out more, see the <a href="/docs/configure-apps/app-reference/composable-image">Composable image</a> topic.
  </Tip>;

<DisclaimerNix />

## Supported versions

You can select the major and minor version.

Patch versions are applied periodically for bug fixes and the like.
When you deploy your app, you always get the latest available patches.

### Ruby

<MetaImageVersionList language="ruby" status="supported" platform="grid" />

<MetaImageVersionList language="ruby" status="incoming" platform="grid" />

### Specify the language

To use Ruby, specify `ruby` as your [app's `type`](/docs/configure-apps/app-reference/single-runtime-image#type):

<DynamicCodeBlock language="yaml" filename=".upsun/config.yaml">
  {`
      applications:
        # The app's name, which must be unique within the project.
        <APP_NAME>:
          type: 'ruby:<VERSION_NUMBER>'
    `
  }
</DynamicCodeBlock>

For example:

<DynamicCodeBlock language="yaml" filename=".upsun/config.yaml">
  {`
      applications:
        # The app's name, which must be unique within the project.
        myapp:
          type: 'ruby:{{version:ruby:latest}}'`
  }
</DynamicCodeBlock>

<VersionDeprecatedBlock />

<MetaImageVersionList language="ruby" status="deprecated" />

## Retired versions

The following versions have been retired and are no longer available.
If your project uses a retired version, you must update to a [supported version](#supported-versions).

<MetaImageVersionList language="ruby" status="retired" />

## Puma based Rails configuration

This example uses Puma to run a Ruby application.
You could use any Ruby application server such as Unicorn.

Configure the `.upsun/config.yaml` file with a few key settings as listed below.
A complete example is included at the end of this section.

1. Specify the language of your application (available versions are listed above):

<DynamicCodeBlock language="yaml" filename=".upsun/config.yaml">
  {`
      applications:
        # The app's name, which must be unique within the project.
        myapp:
          type: 'ruby:{{version:ruby:latest}}'`
  }
</DynamicCodeBlock>

2. Set up environment variables.

   Rails runs by default on a preview environment.
   You can change the Rails/Bundler via those environment variables,
   some of which are defaults on Upsun.

<DynamicCodeBlock language="yaml" filename=".upsun/config.yaml">
  {`
      applications:
        # The app's name, which must be unique within the project.
        myapp:
          type: 'ruby:{{version:ruby:latest}}'
          variables:
            env:
              PIDFILE: "tmp/server.pid" # Allow to start puma directly even if \`tmp/pids\` directory is not created
              RAILS_ENV: "production"
              BUNDLE_WITHOUT: 'development:test'
              TARGET_RUBY_VERSION: '~>{{version:ruby:latest}}' # this will allow to not fail on PATCH update of the image`
  }
</DynamicCodeBlock>

The `SECRET_KEY_BASE` variable is generated automatically based on the
[`PLATFORM_PROJECT_ENTROPY`
variable](/docs/development/variables/use-variables#use-provided-variables) but you can change it.

Based on TARGET\_RUBY\_VERSION, we recommand to set on your Gemfile so next
PATCH release of ruby doesn't fail the build:

```ruby theme={null}
ruby ENV["TARGET_RUBY_VERSION"] || File.read(File.join(File.dirname(__FILE__), ".ruby-version")).strip
```

3. Build your application with the build hook.

   Assuming you have your dependencies stored in the `Gemfile` at [your app root](/docs/configure-apps/app-reference/single-runtime-image#root-directory),
   create a hook like the following:

<DynamicCodeBlock language="yaml" filename=".upsun/config.yaml">
  {`
      applications:
        # The app's name, which must be unique within the project.
        myapp:
          type: 'ruby:{{version:ruby:latest}}'
          ...
          hooks:
            build: |
              set -e
              bundle install
              bundle exec rails assets:precompile
            deploy: bundle exec rake db:migrate`
  }
</DynamicCodeBlock>

These are installed as your project dependencies in your environment.
You can also use the `dependencies` key to install global dependencies.
These can be Ruby, Python, NodeJS, or PHP libraries.

If you have assets, it's likely that you need NodeJS/yarn.

<DynamicCodeBlock language="yaml" filename=".upsun/config.yaml">
  {`
      applications:
        # The app's name, which must be unique within the project.
        myapp:
          type: 'ruby:{{version:ruby:latest}}'
          ...
          dependencies:
            nodejs:
              yarn: "*"`
  }
</DynamicCodeBlock>

4. Configure the command to start serving your application (this must be a foreground-running process) under the `web` section:

<DynamicCodeBlock language="yaml" filename=".upsun/config.yaml">
  {`
      applications:
        # The app's name, which must be unique within the project.
        myapp:
          type: 'ruby:{{version:ruby:latest}}'
          ...
          web:
            upstream:
              socket_family: unix
            commands:
              # for puma
              start: "bundle exec puma -b unix://$SOCKET"
              # for unicorn
              # start: "bundle exec unicorn -l $SOCKET"`
  }
</DynamicCodeBlock>

This assumes you have Puma as a dependency in your Gemfile:

```ruby theme={null}
gem "puma", ">= 5.0"
```

5. Define the web locations your application is using:

<DynamicCodeBlock language="yaml" filename=".upsun/config.yaml">
  {`
      applications:
        # The app's name, which must be unique within the project.
        myapp:
          type: 'ruby:{{version:ruby:latest}}'
          ...
          web:
            locations:
              "/":
                root: "public"
                passthru: true
                expires: 1h
                allow: true`
  }
</DynamicCodeBlock>

This configuration sets the web server to handle HTTP requests at `/static`
to serve static files stored in `/app/static/` folder.
Everything else is forwarded to your application server.

6. Create any Read/Write mounts.

   The root file system is read only.
   You must explicitly describe writable mounts.

<DynamicCodeBlock language="yaml" filename=".upsun/config.yaml">
  {`
      applications:
        # The app's name, which must be unique within the project.
        myapp:
          type: 'ruby:{{version:ruby:latest}}'
          ...
          mounts:
            "/log":
              source: tmp
              source_path: log
            "/storage":
              source: storage
              source_path: storage
            "/tmp":
              source: tmp
              source_path: tmp`
  }
</DynamicCodeBlock>

This setting allows your application writing temporary files to `/app/tmp`,
logs stored in `/app/log`, and active storage in `/app/storage`.

You can define other read/write mounts (your application code itself being deployed to a read-only file system).
Note that the file system is persistent and when you backup your cluster these mounts are also backed up.

7. Then, setup the routes to your application in `.upsun/config.yaml`.

   ```yaml .upsun/config.yaml theme={null}
   applications:
     ...

   routes:
     "https://{default}/":
       type: upstream
       upstream: "myapp:http"
   ```

### Complete app configuration

Here is a complete `.upsun/config.yaml` file:

<DynamicCodeBlock language="yaml" filename=".upsun/config.yaml">
  {`
      # The name of the app, which must be unique within a project.
      applications:
        myapp:
          type: 'ruby:{{version:ruby:latest}}'

          dependencies:
            nodejs:
              yarn: "*"

          relationships:
            mysql:

          variables:
            env:
              BUNDLE_CACHE_ALL: '1' # Default, Cache all gems, including path and git gems.
              BUNDLE_CLEAN: '1' # /!\\ if you are working with Ruby<2.7 this doesn't work well, but should be safe on modern Rubies.
              BUNDLE_DEPLOYMENT: '1' # Default, Disallow changes to the Gemfile.
              BUNDLE_ERROR_ON_STDERR: '1' # Default.
              BUNDLE_WITHOUT: 'development:test'
              PIDFILE: "tmp/server.pid" # Allow to start puma directly even if \`tmp/pids\` directory is not created
              DEFAULT_BUNDLER_VERSION: "2.5.14" # In case none is mentioned in Gemfile.lock
              EXECJS_RUNTIME: 'Node' # If you need one on your assets https://github.com/rails/execjs#readme
              NODE_ENV: 'production'
              NODE_VERSION: v14.17.6
              NVM_VERSION: v0.38.0
              RACK_ENV: 'production'
              RAILS_ENV: 'production'
              RAILS_LOG_TO_STDOUT: '1' # Default
              RAILS_TMP: '/tmp' # Default

          hooks:
            build: |
              set -e

              echo "Installing NVM $NVM_VERSION"
              unset NPM_CONFIG_PREFIX
              export NVM_DIR="$PLATFORM_APP_DIR/.nvm"
              # install.sh will automatically install NodeJS based on the presence of $NODE_VERSION
              curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh | bash
              [ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh"

              # we install the bundled bundler version and fallback to a default (in env vars above)
              export BUNDLER_VERSION="$(grep -A 1 "BUNDLED WITH" Gemfile.lock | tail -n 1)" || "$DEFAULT_BUNDLER_VERSION"
              echo "Install bundler $BUNDLER_VERSION"
              gem install --no-document bundler -v $BUNDLER_VERSION

              echo "Installing gems"
              # We copy the bundle directory to the Upsun cache directory for
              # safe keeping, then restore from there on the next build. That allows
              # bundler to skip downloading code it doesn't need to.
              [ -d "$PLATFORM_CACHE_DIR/bundle" ] && \\
                  rsync -az --delete "$PLATFORM_CACHE_DIR/bundle/" vendor/bundle/
              mkdir -p "$PLATFORM_CACHE_DIR/bundle"
              bundle install
              # synchronize updated cache for next build
              [ -d "vendor/bundle" ] && \\
                  rsync -az --delete vendor/bundle/ "$PLATFORM_CACHE_DIR/bundle/"

              # precompile assets
              echo "Precompiling assets"
              # We copy the webpacker directory to the Upsun cache directory for
              # safe keeping, then restore from there on the next build. That allows
              # bundler to skip downloading code it doesn't need to.
              # https://guides.rubyonrails.org/asset_pipeline.html
              mkdir -p "$PLATFORM_CACHE_DIR/webpacker"
              mkdir -p "$RAILS_TMP/cache/webpacker"
              [ -d "$PLATFORM_CACHE_DIR/webpacker" ] && \\
                  rsync -az --delete "$PLATFORM_CACHE_DIR/webpacker/" $RAILS_TMP/cache/webpacker/
              # We dont need secret here https://github.com/rails/rails/issues/32947
              SECRET_KEY_BASE=1 bundle exec rails assets:precompile
              rsync -az --delete $RAILS_TMP/cache/webpacker/ "$PLATFORM_CACHE_DIR/webpacker/"
            deploy: bundle exec rake db:migrate

          mounts:
            "/log":
              source: tmp
              source_path: log
            "/storage":
              source: storage
              source_path: storage
            "/tmp":
              source: tmp
              source_path: tmp

          web:
            upstream:
              socket_family: unix
            commands:
              # for puma
              start: "bundle exec puma -b unix://$SOCKET"
              # for unicorn
              # start: "bundle exec unicorn -l $SOCKET"

            locations:
              "/":
                root: "public"
                passthru: true
                expires: 1h
                allow: true

      routes:
        "https://{default}/":
          type: upstream
          upstream: "myapp:http"

      services:
        ...`
  }
</DynamicCodeBlock>

## Configuring services

This example assumes there is a MySQL instance.
To configure it, [create a service](/docs/add-services) such as the following:

<DynamicCodeBlock language="yaml">
  {`
      applications:
        ...

      routes:
        ...

      services:
        mysql:
          type: mysql:{{version:mariadb:latest}}`
  }
</DynamicCodeBlock>

## Connecting to services

Once you have a service, link to it in your [app configuration](/docs/configure-apps):

<DynamicCodeBlock language="yaml" filename=".upsun/config.yaml">
  {`
      applications:
        myapp:
          type: 'ruby:{{version:ruby:latest}}'
          relationships:
            mysql:
          [...]

      routes:
        [...]

      services:
        mysql:
          type: mysql:{{version:mariadb:latest}}`
  }
</DynamicCodeBlock>

By using the following Ruby function calls, you can obtain the database details.

```ruby theme={null}
require "base64"
require "json"
relationships= JSON.parse(Base64.decode64(ENV['PLATFORM_RELATIONSHIPS']))
```

This should give you something like the following:

```json theme={null}
{
  "mysql" : [
    {
      "path" : "main",
      "query" : {
        "is_master" : true
      },
      "port" : 3306,
      "username" : "user",
      "password" : "",
      "host" : "mysql.internal",
      "ip" : "246.0.241.50",
      "scheme" : "mysql"
    }
  ]
}
```

For Rails, you can use the standard Rails `config/database.yml` with the values found with the snippet provided before.

## Other tips

* To speed up boot you can use the [Bootsnap gem](https://github.com/Shopify/bootsnap)
  and configure it with the local `/tmp`:

  ```ruby config/boot.rb theme={null}
  Bootsnap.setup(cache_dir: "/tmp/cache")
  ```

* For garbage collection tuning, you can read [this article](https://shopify.engineering/17489064-tuning-rubys-global-method-cache)
  and look for [discourse configurations](https://github.com/discourse/discourse_docker/blob/b259c8d38e0f42288fd279c9f9efd3cefbc2c1cb/templates/web.template.yml#L8)

* New images are released on a regular basis to apply security patches. While the minor version will not change (as you are specifying it in the `type` property), the patch version will be updated. You may encounter this kind of error:

  ```
  bundler: failed to load command: puma (/app/vendor/bundle/ruby/3.2.0/bin/puma)
  /app/.global/gems/bundler-2.4.22/lib/bundler/definition.rb:447:in `validate_ruby!': Your Ruby version is 3.2.9, but your Gemfile specified 3.2.8 (Bundler::RubyVersionMismatch)
  ```

  To avoid issues when such updates are performed, use

  ```ruby theme={null}
  ruby ENV["TARGET_RUBY_VERSION"] || File.read(File.join(File.dirname(__FILE__), ".ruby-version")).strip
  ```

  in your `Gemfile`, where `TARGET_RUBY_VERSION` has been defined as above.

<RepoList lang="ruby" displayName="Ruby" />

## Troubleshooting

By default, deployments have `BUNDLE_DEPLOYMENT=1` to ensure projects have a `Gemfile.lock` file.
This is safer for version yank issues and other version upgrade breakages.

You may encounter an error like the following during a build:

```txt {no-copy="true"} theme={null}
W: bundler: failed to load command: rake (/app/.global/bin/rake)
W: /app/.global/gems/bundler-2.3.5/lib/bundler/resolver.rb:268:in `block in verify_gemfile_dependencies_are_found!': Could not find gem 'rails (= 5.2.6)' in locally installed gems. (Bundler::GemNotFound)
```

To resolve this error:

1. Run `bundle install` with the same `ruby` and `bundler` versions defined in your `.upsun/config.yaml` file.
2. Push the `Gemfile.lock` to your repository.
