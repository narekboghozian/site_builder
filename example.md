All lines until first '#' line (title) will be ignored or used as metadata.

Metadata is in the format:
/<item> <value> // <comment>

Content after a ' //' will be considered as a comment. ('//' without preceding whitespace will not count as a comment)

So an example would be:
/date 12.31.2020

Required parameters:
/date 12.31.2020 // 'date' in the 'mm.dd.yyyy' format
/title Document Title

Optional parameters are:
/toc true // Table of contents. Default is true
/description This is a description that if given, will override the defualt usage of the first <p> after the first <h1> title element
/tag tag1 tag2 tag3 etc // add tags like this

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
