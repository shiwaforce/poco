# POCO
[![Build Status](https://travis-ci.org/shiwaforce/poco.svg?branch=command-refactor)](https://travis-ci.org/shiwaforce/poco)
[![pypi](https://img.shields.io/pypi/v/poco.svg)](https://pypi.python.org/pypi/poco)
[![python](https://img.shields.io/pypi/pyversions/poco.svg)](https://pypi.python.org/pypi/poco)

<p align="center">
  <img width="200" height="200" title="Poco Logo" src="https://raw.githubusercontent.com/shiwaforce/poco/command-refactor/logo.jpg"/>
</p>

`poco` is a docker missing tool. With it's help you will be able to manage docker or kubernetes projects of any complexity with ease. 
It is just indispensable tool for any kind of projects from small to large.
You can use `poco` for development and for demo purposes as well.


[Video](https://asciinema.org/a/137172)
[Example](https://github.com/shiwaforce/poco-example)

## Requirements
- Docker, version > 17, if you want use Docker-compose files
- kubectl, if you want use Kubernetes


## Getting started
#### Install `poco`:
```
$:~ pip install poco
```

#### Create `poco` project:
```
$:~ mkdir poco-project
$:~ cd poco-project
$:~ poco init
```
`poco.yml` and `docker-compose.yml` example files will be created.

#### Start `poco` project:
```
$:~ poco start
```

#### Create `poco repo`:
```
$:~ poco repo init
```
Sample catalog will be initialised with the default environment

#### Add remote catalog
```
$:~ poco repo add <name> <git-ssh-url> [<branc>] [<file>]
```

#### Add `poco` project into catalog:
```
$:~ poco project add [<target-dir>] [<catalog>]
```

#### Publish (push) `poco repo`:
```
$:~ poco repo push
```

#### Stop `poco` project:
```
$:~ poco stop
```


## Terminology 
`poco` - .   
`poco repo` - .  
`poco project` - .  
`plan` -


## Commands
##### poco:
<table width="100%">
    <tr>
        <td width="40%"><b>Command</b></td>
        <td width="30%"><b>Parameters</b></td>
        <td width="30%"><b>Description</b></td>
    </tr>
    <tr>
        <td><b><code>$:~ poco project-config [&lt;project&gt;] [&lt;plan&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
            <p><code>[&lt;plan&gt;]</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Print full Docker compose configuration for a project's plan.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco clean</code></b></td>
        <td>-</td>
        <td>
            <p>Clean all containers and images from the local Docker repository.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco init [&lt;project&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
        </td>
        <td>
            <p>Initialize poco project, poco.yml and docker-compose.yml will be created if they don't exist.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco install [&lt;project&gt;] [&lt;plan&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
            <p><code>[&lt;plan&gt;]</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Clone projects from a remote repository, run install scripts.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco (start|up) [&lt;project&gt;] [&lt;plan&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
            <p><code>[&lt;plan&gt;]</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Start poco project with the default or defined plan.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco (stop|down) [&lt;project&gt;] [&lt;plan&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
            <p><code>[&lt;plan&gt;]</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Stop project with the default or defined plan.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco restart [&lt;project&gt;] [&lt;plan&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
            <p><code>[&lt;plan&gt;]</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Restart project with the default or defined plan.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco (log|logs) [&lt;project&gt;] [&lt;plan&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
            <p><code>[&lt;plan&gt;]</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Print docker containers logs of the current project with the default or defined plan.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco build [&lt;project&gt;] [&lt;plan&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
            <p><code>[&lt;plan&gt;]</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Build containers depends defined project and plan.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco ps [&lt;project&gt;] [&lt;plan&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
            <p><code>[&lt;plan&gt;]</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Print containers statuses which depends defined project and plan.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco plan ls [&lt;project&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
        </td>
        <td>
            <p>Print all available plans of the project.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco pull [&lt;project&gt;] [&lt;plan&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
            <p><code>[&lt;plan&gt;]</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Pull all necessary images for the project with the defined or default plan.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco branches [&lt;project&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
        </td>
        <td>
            <p>List all available git branches of the project.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco pack [&lt;project&gt;] [&lt;plan&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
            <p><code>[&lt;plan&gt;]</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Pack the selected project's plan configuration with docker images into an archive.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco unpack [&lt;project&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project in the catalog</p>
            <p><code>[&lt;plan&gt;]</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Unpack archive, install images to local repository.</p>
        </td>
    </tr>
</table>

##### poco repo:
<table width="100%">
    <tr>
        <td width="40%"><b>Command</b></td>
        <td width="30%"><b>Parameters</b></td>
        <td width="30%"><b>Description</b></td>
    </tr>
    <tr>
        <td><b><code>$:~ poco repo init</code></b></td>
        <td>
            -
        </td>
        <td>
            <p>Initialize default environment and sample catalog.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco repo ls</code></b></td>
        <td>-</td>
        <td>
            <p>List the configs of catalogs.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~  poco repo (add|modify) &lt;name&gt; &lt;git-url&gt; [&lt;branch&gt;] [&lt;file&gt;]</code></b></td>
        <td>
            <p><code>&lt;name&gt;</code> - Name of the catalogue.</p>
            <p><code>&lt;git-url&gt;</code> - URL of catalog's GIT repository.</p>
            <p><code>[&lt;branch&gt;]</code> - Name of the branch that should be checked out. (default : master)</p>
            <p><code>[&lt;file&gt;]</code> - Name of the catalog file in the repository. (default: poco-catalog.yml)</p>
        </td>
        <td>
            <p>Add/Modify new catalog to the config.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco repo (remove|rm) &lt;name&gt;</code></b></td>
        <td>
            <p><code>&lt;name&gt;</code> - Name of the catalog.</p>
        </td>
        <td>
            <p>Remove catalog from local config.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco repo branch &lt;branch&gt; [&lt;name&gt;] [-f]</code></b></td>
        <td>
            <p><code>&lt;branch&gt;</code> - Name of the branch that should be checked out.</p>
            <p><code>[&lt;name&gt;]</code> - Name of the catalog.</p>
            <p><code>-f</code> - Name of the project's plan</p>
        </td>
        <td>
            <p>Switch catalog branch if it is using GIT.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco repo branches [&lt;name&gt;]</code></b></td>
        <td>
            <p><code>[&lt;name&gt;]</code> - Name of the catalog.</p>
        </td>
        <td>
            <p>List all available branches of catalog's GIT repository.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco repo push [&lt;name&gt;]</code></b></td>
        <td>
            <p><code>name</code> - Name of the catalog.</p>
        </td>
        <td>
            <p>Push changes into catalog's remote GIT repository</p>
        </td>
    </tr>
</table>

##### poco project:
<table width="100%">
    <tr>
        <td width="40%"><b>Command</b></td>
        <td width="30%"><b>Parameters</b></td>
        <td width="30%"><b>Description</b></td>
    </tr>
    <tr>
        <td><b><code>$:~ poco project add [&lt;target-dir&gt;] [&lt;catalog&gt;]</code></b></td>
        <td>
            <p><code>[&lt;target-dir&gt;]</code> - Target directory that will be added to the catalog. Default is the current directory.</p>
            <p><code>[&lt;catalog&gt;]</code> - Name of the catalog.</p>
        </td>
        <td>
            <p>Add directory to catalog.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco project init [&lt;project&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project that will be added to the catalog</p>
        </td>
        <td>
            <p>Create poco.yml and docker-compose.yml to a project if aren't exists.</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco project ls</code></b></td>
        <td>
            -
        </td>
        <td>
            <p>List all projects from the catalog(s).</p>
        </td>
    </tr>
    <tr>
        <td><b><code>$:~ poco project remove [&lt;project&gt;]</code></b></td>
        <td>
            <p><code>[&lt;project&gt;]</code> - Name of the project that will be removed</p>
        </td>
        <td>
            <p>Remove project from the catalog.</p>
        </td>
    </tr>
</table>
