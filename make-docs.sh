#!/bin/bash

TMP_DIR=/tmp/pypln-docs
GH_PAGES=0
VERBOSE=0
HELP=0
LOCAL=0

function show_help() {
    echo "Usage: $0 [-d|-D] [-g|-G] [-v[v]] [-p <path>]"
    echo
    echo "  [-d|-D]      Use (-d) 'develop' branch (without uncommitted changes)"
    echo "               to build docs. -D will use current branch with"
    echo "               uncommitted changes. Default: -d"
    echo
    echo "  [-g|-G]      Enable/disable committing changes to branch 'gh-pages'"
    echo "               after building docs. Default: -G (disabled)"
    echo
    echo "  [-v[v]]      Verbose mode. Default: None"
    echo "               None = no output"
    echo "               -v   = show status messages"
    echo "               -vv  = show status messages + build messages"
    echo
    echo "  [-p <path>]  Path in which docs will be built. Default: $TMP_DIR"
}

set -- `getopt hdDgGvp: "$@" 2> /dev/null`
while [ $# -gt 0 ]; do
    case $1 in
        -h)
            HELP=1
            show_help
           exit 0
           ;;
        -d)
            LOCAL=0
            ;;
        -D)
            LOCAL=1
            ;;
        -g)
            GH_PAGES=1
            ;;
        -G)
            GH_PAGES=0
            ;;
        -v)
            VERBOSE=$(($VERBOSE + 1))
            ;;
        -p)
            if [ ${2:0:1} = "-" ]; then
                echo 'ERROR: you must specify a path'
                exit 1
            fi
            TMP_DIR=$2
            shift
            ;;
    esac
    shift
done

if [ $GH_PAGES -eq 1 ] && [ $LOCAL -eq 1 ]; then
    echo "ERROR: you can only commit to 'gh-pages' branch when building from 'develop' branch"
    exit 1
fi

function log() {
    if [ $VERBOSE -gt 0 ]; then
        echo "*** [$(date +'%Y-%m-%d %H:%M:%S')] $@"
    fi
}

function build_sphinx() {
    cd doc
    make html
    cd ..
    mv doc/_build/html/* $TMP_DIR/
    rm -rf doc/_build
}

function build_epydoc() {
    epydoc -v -u https://github.com/namd/pypln.backend --debug --graph=all \
           --parse-only --html --no-frames -o $TMP_DIR/reference pypln/
}

log 'Creating temporary directory to store static files...'
rm -rf $TMP_DIR
mkdir $TMP_DIR
cp .gitignore $TMP_DIR/

if [ $LOCAL -eq 0 ]; then
    log 'Stashing changes (if needed)...'
    current_branch=$(git branch | grep '*' | cut -d ' ' -f 2)
    stashes_before=$(git stash list | wc -l)
    git stash save -u "temporary stash to build docs" &> /dev/null || \
        { echo "Can't stash your changes"; exit 1; }
    stashes_after=$(git stash list | wc -l)
    log "Checking out to branch 'develop'"
    git checkout develop &> /dev/null
fi

# Make Sphinx documentation from 'develop' branch
log "Building Sphinx documentation..."
if [ $VERBOSE -gt 1 ]; then
    build_sphinx || \
        { echo "can't generate sphinx documentation"; exit 1; }
else
    build_sphinx 2&> /dev/null || \
        { echo "can't generate sphinx documentation"; exit 1; }
fi

# Make Reference documentation using epydoc
log 'Building API Reference with epydoc...'
if [ $VERBOSE -gt 1 ]; then
    build_epydoc || \
        { echo "Can't generate epydoc documentation"; exit 1; }
else
    build_epydoc 2&> /dev/null || \
        { echo "Can't generate epydoc documentation"; exit 1; }
fi

if [ "$GH_PAGES" -eq 1 ]; then
    log "Storing and committing changes on branch 'gh-pages'..."
    git checkout gh-pages &> /dev/null
    rm -rf *
    mv $TMP_DIR/* $TMP_DIR/.gitignore .
    touch .nojekyll
    rm -rf $TMP_DIR
    git add . &> /dev/null
    git commit -m 'Docs built automatically by make-docs.sh' &> /dev/null
    log "Checking out to branch '$current_branch'"
    git checkout $current_branch &> /dev/null
else
    log "Documentation generated at: $TMP_DIR"
fi

if [ "$stashes_after" != "$stashes_before" ]; then
    log 'Applying stash...'
    git stash pop &> /dev/null
fi

log 'Finished!'
