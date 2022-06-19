All lines until first '#' line (title) will be ignored or used as metadata.

Metadata is in the format:
/<item>=<value>

Without spaces. After the <value>, content after a space can be added to make a comment. Spaces in quotes are considered as part of the quoted string. (It's good practice to put // before any comments to make them visually distinct)

So an example would be:
/date=12.31.2020

Required parameters:
/date=12.31.2020 // 'date' in the 'mm.dd.yyyy' format

Optional parameters are:
/toc=true // Table of contents. Default is true
/description="This is a description that if given, will override the defualt usage of the first <p> after the first <h1> title element"

# Example Page Title

This first line of content after the example page title will be the description used in the RSS feed.

## Scope

### Objective

### Deliverables

### Milestones

### Requirements

### Constraints

### Assumptions

### Exclusions
