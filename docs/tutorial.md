# Tutorial System

YouTrack CLI includes an interactive tutorial system designed to help new users learn the CLI through guided, hands-on experiences. The tutorial system covers essential workflows and best practices with step-by-step instructions.

## Overview

The tutorial system provides:

- **Interactive Learning**: Step-by-step guidance through common workflows
- **Progress Tracking**: Automatic saving of tutorial progress with resume capability
- **Real-world Examples**: Practical commands and scenarios you'll use daily
- **Beginner-friendly**: Clear explanations and helpful tips throughout

## Available Tutorials

### Setup Tutorial (`setup`)
Learn how to authenticate and configure YouTrack CLI for first use. This tutorial covers:
- Understanding YouTrack CLI capabilities
- Setting up authentication with API tokens
- Verifying your connection
- Configuring optional settings

### Issues Tutorial (`issues`)
Master issue management with the CLI. This tutorial covers:
- Understanding YouTrack issues
- Listing and filtering issues
- Creating new issues
- Viewing detailed issue information
- Updating issues and their status

### Projects Tutorial (`projects`)
Learn to work with YouTrack projects effectively. This tutorial covers:
- Understanding project structure
- Exploring available projects
- Viewing project details and configuration
- Working with project-specific custom fields

### Time Tracking Tutorial (`time`)
Master time tracking for project management. This tutorial covers:
- Understanding time tracking concepts
- Logging work time against issues
- Viewing time entries and reports
- Best practices for time tracking

## Using the Tutorial System

### List Available Tutorials

View all available tutorials and their progress:

```bash
yt tutorial list
```

Add the `--show-progress` flag to see detailed completion statistics:

```bash
yt tutorial list --show-progress
```

### Run a Tutorial

Start a tutorial from the beginning:

```bash
yt tutorial run setup
```

Resume a tutorial from a specific step:

```bash
yt tutorial run issues --step 3
```

Reset and restart a tutorial:

```bash
yt tutorial run projects --reset
```

### Manage Tutorial Progress

View detailed progress for all tutorials:

```bash
yt tutorial progress
```

Reset progress for a specific tutorial:

```bash
yt tutorial reset issues
```

Reset all tutorial progress:

```bash
yt tutorial reset --all
```

### Provide Feedback

Share feedback about the tutorial system:

```bash
yt tutorial feedback
```

## Tutorial Features

### Interactive Navigation

During a tutorial, you can:
- **Next**: Continue to the next step
- **Repeat**: Review the current step again
- **Skip**: Skip the current step and move forward
- **Quit**: Exit the tutorial (progress is saved automatically)

### Progress Persistence

- Tutorial progress is automatically saved
- You can safely exit and resume tutorials later
- Progress is stored in `~/.config/youtrack-cli/tutorial_progress.json`
- Each tutorial tracks completed steps and current position

### Step-by-Step Guidance

Each tutorial step includes:
- Clear title and description
- Detailed instructions
- Example commands to try
- Helpful tips and best practices
- Troubleshooting guidance

## Tips for Success

1. **Take Your Time**: Tutorials are self-paced - don't rush through them
2. **Try the Commands**: Execute the example commands in your terminal
3. **Read the Tips**: Each step includes helpful tips and best practices
4. **Use Real Data**: When possible, work with real YouTrack projects and issues
5. **Ask Questions**: Use the feedback command to report issues or suggestions

## Troubleshooting

### Tutorial Won't Start
- Ensure YouTrack CLI is properly installed
- Check that you have the latest version
- Try resetting the tutorial progress

### Progress Not Saving
- Verify write permissions to `~/.config/youtrack-cli/`
- Check available disk space
- Try manually creating the config directory

### Commands Not Working
- Ensure you're authenticated with `yt auth login`
- Verify your YouTrack instance is accessible
- Check that you have appropriate permissions

## Advanced Usage

### Custom Tutorial Content

While the built-in tutorials cover essential workflows, you can extend your learning by:
- Exploring advanced command options with `--help`
- Reading the full documentation
- Experimenting with different YouTrack projects
- Combining commands in scripts

### Integration with Other Learning

The tutorial system complements other learning resources:
- CLI help system (`yt --help`, `yt COMMAND --help`)
- Online documentation
- YouTrack API documentation
- Community examples and scripts

## Getting Help

If you need help with the tutorial system:

1. Use `yt tutorial --help` for command reference
2. Check the troubleshooting section above
3. Report issues at https://github.com/ryancheley/yt-cli/issues
4. Provide feedback with `yt tutorial feedback`

The tutorial system is designed to make learning YouTrack CLI enjoyable and effective. Take advantage of the interactive features and don't hesitate to revisit tutorials as needed!
