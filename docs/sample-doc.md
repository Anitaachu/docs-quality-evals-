# Ruby

Supports deploying any Ruby application. Your application can use any Ruby application server such as Puma or Unicorn and deploying a Rails or a Sinatra app is very straight forward.

## Supported versions

You can select the major and minor version. Patch versions are applied periodically for bug fixes and the like. When you deploy your app, you always get the latest available patches.

### Ruby

### Specify the language

To use Ruby, specify `ruby` as your app's `type`. For example:

## Retired versions

The following versions have been retired and are no longer available. If your project uses a retired version, you must update to a supported version.

## Puma based Rails configuration

This example uses Puma to run a Ruby application. You could use any Ruby application server such as Unicorn. Configure the `.upsun/config.yaml` file with a few key settings as listed below. A complete example is included at the end of this section.

1. Specify the language of your application (available versions are listed above):

2. Set up environment variables. Rails runs by default on a preview environment. You can change the Rails/Bundler via those environment variables, some of which are defaults on Upsun. The `SECRET_KEY_BASE` variable is generated automatically based on the `PLATFORM_PROJECT_ENTROPY` variable but you can change it. Based on TARGET_RUBY_VERSION, we recommand to set on your Gemfile so next PATCH release of ruby doesn't fail the build:
3. Build your application with the build hook. Assuming you have your dependencies stored in the `Gemfile` at your app root, create a hook like the following:

   These are installed as your project dependencies in your environment. You can also use the `dependencies` key to install global dependencies. These can be Ruby, Python, NodeJS, or PHP libraries. If you have assets, it's likely that you need NodeJS/yarn.

4. Configure the command to start serving your application (this must be a foreground-running process) under the `web` section. This assumes you have Puma as a dependency in your Gemfile:
5. Define the web locations your application is using. This configuration sets the web server to handle HTTP requests at `/static` to serve static files stored in `/app/static/` folder. Everything else is forwarded to your application server.

6. Create any Read/Write mounts. The root file system is read only. You must explicitly describe writable mounts. This setting allows your application writing temporary files to `/app/tmp`, logs stored in `/app/log`, and active storage in `/app/storage`. You can define other read/write mounts (your application code itself being deployed to a read-only file system). Note that the file system is persistent and when you backup your cluster these mounts are also backed up.

7. Then, setup the routes to your application in `.upsun/config.yaml`:

```yaml
   applications:
     ...

   routes:
     "https://{default}/":
       type: upstream
       upstream: "myapp:http"
```

### Complete app configuration

Here is a complete `.upsun/config.yaml` file.

## Configuring services

This example assumes there is a MySQL instance. To configure it, create a service such as the following.

## Connecting to services

Once you have a service, link to it in your app configuration. By using the following Ruby function calls, you can obtain the database details:
This should give you something like the following:

```yaml
applications:
  myapp:
    type: 'ruby:4.0'
    relationships:
      mysql:
    [...]

routes:
  [...]

services:
  mysql:
    type: mysql:11.8

```

For Rails, you can use the standard Rails `config/database.yml` with the values found with the snippet provided before.

## Other tips


- To speed up boot you can use the Bootsnap gem and configure it with the local `/tmp`:
- For garbage collection tuning, you can read this article and look for discourse configurations.

- New images are released on a regular basis to apply security patches. While the minor version will not change (as you are specifying it in the `type` property), the patch version will be updated. You may encounter this kind of error:

```
bundler: failed to load command: puma (/app/vendor/bundle/ruby/3.2.0/bin/puma)
/app/.global/gems/bundler-2.4.22/lib/bundler/definition.rb:447:in `validate_ruby!': Your Ruby version is 3.2.9, but your Gemfile specified 3.2.8 (Bundler::RubyVersionMismatch)
```
To avoid issues when such updates are performed, use:
```
ruby ENV["TARGET_RUBY_VERSION"] || File.read(File.join(File.dirname(FILE), ".ruby-version")).strip

```
in your `Gemfile`, where `TARGET_RUBY_VERSION` has been defined as above.

## Troubleshooting

By default, deployments have `BUNDLE_DEPLOYMENT=1` to ensure projects have a `Gemfile.lock` file. This is safer for version yank issues and other version upgrade breakages. You may encounter an error like the following during a build:
```
W: bundler: failed to load command: rake (/app/.global/bin/rake)
W: /app/.global/gems/bundler-2.3.5/lib/bundler/resolver.rb:268:in `block in verify_gemfile_dependencies_are_found!': Could not find gem 'rails (= 5.2.6)' in locally installed gems. (Bundler::GemNotFound)
```
To resolve this error:

1. Run `bundle install` with the same `ruby` and `bundler` versions defined in your `.upsun/config.yaml` file.
2. Push the `Gemfile.lock` to your repository.
