import re, sublime, sublime_plugin

# Take note if we're in ST3 so that we can do ST3 specific stuff
# (Currently unused, this line is left in, because I think it's handy to have around)
ST3 = sublime.version() >= '3000'

class SelectByRegexCommand(sublime_plugin.TextCommand):
    original_regions = []
    history = [ "" ]
    history_index = 0
    
    def description():
        """
        Part of the plugin API, description returns a string describing a command
        """
        return 'Split the current line (or selection) by a (prompted) regular expression'
        
    def on_cancel(self): 
        """
        Event handler for input, called when users cancells
        """
        # Restore the original selection
        self.restore_selection()
    
    def on_change(self, text):
        """
        Event handler for input, called when user changes the text in the field
        
        :param text: The current text of the input field
        """
        # Don't process empty text
        if not text: return
        # Perform select by regex
        else: self.update_selection(text, draw_borders=True)

    def on_done(self, text):
        """
        Event handler for input, called when user presses return or submits the field 
        
        :param text: The current text of the input field
        """
        # If empty input, then deselect all
        if not text: self.restore_selection()
        else: 
            # Perform select by regex
            self.update_selection(text, draw_borders=False)
            # Save the selection for next time
            SelectByRegexCommand.history.append(text)
            # Reset the history to the end (technically beginning)
            SelectByRegexCommand.history_index = 0
    
    def restore_selection(self):
        """
        Put the selection of the current view back to what it was before all this madness began
        """
        # Obtain the selection from the view
        selection = self.view.sel()
        # Clear the current selection
        selection.clear()
        # Select all the originals
        selection.add_all(SelectByRegexCommand.original_regions)
        # Clear the bordered regions
        self.view.erase_regions("SelectByRegexCommand")
                
    def run(self, edit):
        """
        Part of the plugin api, called when the command is executed
        
        :param edit: The current edit for tracking undo operations
        """
        # Initialize the original regions
        SelectByRegexCommand.original_regions = []
        # Store all the regions in the selection into the originals
        for region in self.view.sel(): 
            SelectByRegexCommand.original_regions += [ sublime.Region(region.a, region.b) ]
        # Show the user input prompt asking for a regex
        SelectByRegexCommand.input_view = self.view.window().show_input_panel('Regex:', '', 
            # On Done
            self.on_done,
            # On Change
            self.on_change,
            # On Cancel
            self.on_cancel
            )
        # Set a TMLanguage to give the input view a context, keybindings, etc.
        SelectByRegexCommand.input_view.set_syntax_file('Packages/Select By Regex/SelectByRegex.hidden-tmLanguage')
        SelectByRegexCommand.input_view.settings().set("is_widget", True);
        SelectByRegexCommand.input_view.settings().set("gutter", False);
        SelectByRegexCommand.input_view.settings().set("rulers", []);
    
    def update_selection(self, regex, draw_borders=True):
        """
        Perform the search and change the selection to all regions matching the regex which are also contained in the 
        original region(s)
        
        :param regex: The regular expression for which to search
        """
        # Don't process empty searches
        if not regex: return
        # Cache view for speed
        view = self.view
        # Initialize our array of results
        new_regions = []
        # Run this command on each region
        for region in SelectByRegexCommand.original_regions:
            # If this region is backwards, then flip it
            if(region.b < region.a): region = sublime.Region(region.b, region.a)
            # If the region is empty, then select the whole line
            if(region.size() == 0): region = view.line(region)
            # Initialize our search cursor to the beginning of the region region
            caret = region.a
            
            while(caret < region.b):
                # Find the next instance of the regex
                match = view.find(regex, caret)
                # If the match is zero-length, then increment the caret and continue
                if not match: caret += 1
                else:
                    # Check to see if the match is in the current region
                    if(region.contains(match)): new_regions += [ match ]
                    # Move the caret past this region
                    caret = match.b
        # Empty the selection
        view.sel().clear()
        # Draw borders around the matches    
        if(draw_borders):
            # If there are items in our new regions list, then change the selection to those
            if(len(new_regions)):
                # Get the scope for the first region
                scope = view.scope_name(new_regions[0].a)
                # Highlight all the regions with that scope
                view.add_regions("SelectByRegexCommand", new_regions, scope, "", sublime.DRAW_NO_FILL) # Select the matches
            # Erase the borders and select the regions
            else: view.erase_regions("SelectByRegexCommand")
        else: 
            # Skip empty regions, because that would empty the selection (annoying)
            if len(new_regions): 
                # Add each selection to the view
                for region in new_regions: view.sel().add(region)
            # If not regions, then select the original regions
            else: view.sel().add_all(SelectByRegexCommand.original_regions)
            # Erase the borders and select the regions
            view.erase_regions("SelectByRegexCommand")

class SelectByRegexHistoryCommand(sublime_plugin.TextCommand):
    def run(self, edit, backwards=False):
        # Either go forwards or backwards
        increment = [1, -1][backwards]
        # Increment the history
        SelectByRegexCommand.history_index += increment
        # Wrap the history
        SelectByRegexCommand.history_index %= len(SelectByRegexCommand.history)
        # Replace the text with the item from history
        self.view.replace(edit, sublime.Region(0, self.view.size()), SelectByRegexCommand.history[SelectByRegexCommand.history_index])
        