# --------------------------------------------------------------------------------
# Script Name: "Joint" Class from "autoRig" for Maya
# Description: This script manages the creation, deletion, and manipulation ofjoints in Maya,
#              including mirroring and creating bones. It features a class-based structure with
#              UI elements for interactive joint management within Maya's environment.
# Author: Kai Mallari
# Created: February 2024
# --------------------------------------------------------------------------------

import maya.cmds as mc
import webbrowser
import time

# UI Elements
green_check_icon = "\U00002705"  # Indicates a completed state; used with indicator light
orange_square_icon = "\U0001F7E7"  # Indicates an incomplete state; used with indicator light
delete_icon = "\U0001F5D1"
button_height = 25  # Standard height for UI buttons to maintain consistency

time_sleep: float = 0.05  # Prevents program from skipping steps by running too fast


# Class to manage joint creation, deletion, and operations in Maya.
class Joint:
    """
    Manages the creation and deletion of joints in Maya.
    Attributes:
        name (str): The name of the joint, starting with a capital letter and using underscores for spaces.
                    Becomes the joint name in the Maya Outliner.
        mirrored_name (str): The name for mirrored joints, prefixed with "Mirrored_".
        indicator_label (str): UI label for the joint's indicator light.
        x1_coord, y1_coord, z1_coord (float): XYZ coordinates of the joint.
        x2_coord, y2_coord, z2_coord (float): XYZ coordinates of the mirrored joint.
        indicator_light (bool): Indicator light status, controls joint creation flow.
        help_url (str): URL to relevant documentation.
    Parameters:
        name (str): The name of the joint.
        url (str): The URL to the joint's documentation.
    """
    # Initializes a new Joint instance
    def __init__(self, name, url):
        self.name = name
        self.mirrored_name = f"Mirrored_{name}"
        self.indicator_label = f"{str(name).lower()}_indicator"
        self.x1_coord = None
        self.y1_coord = None
        self.z1_coord = None
        self.x2_coord = None
        self.y2_coord = None
        self.z2_coord = None
        self.indicator_light = False
        self.help_url = url

    # Opens the documentation URL in a web browser
    def get_help(self):
        """
        Opens the joint's documentation URL in the default web browser.

        Utilizes the `webbrowser` module to open the URL stored in `help_url`.
        """
        webbrowser.open(self.help_url)

    # Turns the joint's indicator light on if it's currently off
    def indicator_light_on(self):
        """
        Turns the joint's indicator light on, signifying that a joint has been created.

        If the indicator light is already on, a message is printed to the console.

        Updates the UI button label to display the green check icon.

        Affects the UI representation of the joint's status but does not alter the joint itself.
        """
        if self.indicator_light is True:
            print(f"\nThe {self.name} indicator light is already on!")
        else:
            mc.button(self.indicator_label, edit=True, label=green_check_icon)
            self.indicator_light = True
            print(f"\nYou turned the {self.name} indicator light on")

    # Turns the joint's indicator light off if it's currently on
    def indicator_light_off(self):
        """
        Turns the joint's indicator light off, signifying that no joint exists, or it has been deleted.

        If the indicator light is already off, a message is printed to the console.

        Updates the UI button label to display the orange square icon.

        Affects the UI representation of the joint's status but does not alter the joint itself.
        """
        if self.indicator_light is False:
            print(f"\nThe {self.name} indicator light is already off!")
        else:
            mc.button(self.indicator_label, edit=True, label=orange_square_icon)
            self.indicator_light = False
            print(f"\nYou turned the {self.name} indicator light off")

    # Main action handler for joint operations
    def main_button(self):
        """
        Main handler for joint creation operations triggered by the UI.

        Requires an active Vertex Selection within Maya. Creates a joint inside Maya.

        Checks the indicator light status to prevent creating duplicate joints for the same name.
        If no vertices are selected or the indicator light is already on, indicating a joint exists,
        it provides feedback through console messages. Otherwise, it proceeds to calculate the
        average position from the selected vertices to place the new joint.
        """
        if self.indicator_light is True:
            print(f"\nYou already have a {self.name} Joint. Please delete the existing Joint before creating another.")
        else:
            if not bool(mc.ls(selection=True, flatten=True)):  # Checks if we have no active selection
                print("\nYou haven't selected anything. Please make a selection.")
            else:  # Runs if we have an active selection
                self.get_average_xyz()

    # Calculates the average position from selected vertices and creates a joint there
    def get_average_xyz(self):
        """
        Calculates the average XYZ coordinates from the currently selected vertices and places a joint
        at that average position.

        This method is integral to the joint creation process, ensuring joints are positioned accurately
        based on the user's selection in Maya. It fetches the current vertex selection, computes the
        average position, and creates a joint at this location, updating the joint's stored coordinates.
        """
        selected_verts = mc.ls(selection=True, flatten=True)

        print(f"\nYou've selected {len(selected_verts)} vertices")

        # Placeholder variables to store the total sum of X, Y, and Z values
        total_x = 0.0
        total_y = 0.0
        total_z = 0.0

        # Iterate over each vertex to sum up their X, Y, and Z values
        for vertex in selected_verts:
            pos = mc.pointPosition(vertex, world=True)
            total_x += pos[0]
            total_y += pos[1]
            total_z += pos[2]

        # Calculate the average by dividing the total sum by the number of vertices
        num_vertices = len(selected_verts)
        average_x = total_x / num_vertices
        average_y = total_y / num_vertices
        average_z = total_z / num_vertices

        # Save the average XYZ coords to the Joint XYZ coords
        self.y1_coord = average_y
        self.z1_coord = average_z
        self.x1_coord = average_x

        # Create the joint
        mc.joint(name=self.name, position=(self.x1_coord, self.y1_coord, self.z1_coord))
        self.indicator_light_on()

    # Handles the deletion of a joint through the UI
    def delete_joint_button(self):
        """
        Handles the deletion of the joint associated with this instance when triggered from the UI.

        Verifies the existence of the joint in the Maya scene before attempting deletion.

        Checks for and clears any stored coordinate data and updates the UI to reflect the deletion.
        """
        if not mc.objExists(self.name):  # Runs if the joint does not exist
            print(f"Joint '{self.name}' does not exist in the scene.")
            self.clear_coords()
        else:  # Runs if the joint exists
            self.delete_joint()
            self.clear_coords()

    # Clears the stored XYZ coordinates for the joint
    def clear_coords(self):
        """
        Ensures the joint's data is fully reset and does not interfere with subsequent joint creations.

        Clears the stored XYZ coordinates for this joint instance.
        Verifies if the joint has stored coordinate data before attempting
        to clear it to prevent an error deleting "None" data.
        """
        if self.x1_coord is None:
            print(f"No coordinates currently exist for the {self.name} Joint")
        else:
            print(f"\nDeleting saved X coordinates for {self.name}")
            self.x1_coord = None
            self.x2_coord = None
            print(f"Deleting saved y coordinates for {self.name}")
            self.y1_coord = None
            self.y2_coord = None
            print(f"Deleting saved Z coordinates for {self.name}")
            self.z1_coord = None
            self.z2_coord = None
            self.indicator_light_off()
            print(f"Coordinates for the '{self.name}' Joint have been deleted.")

    # Deletes the joint from the Maya scene (and mirrored joint)
    def delete_joint(self):
        """
        Deletes the joint from the Maya scene, along with any mirrored version if it exists.

        This method ensures that both the original and mirrored joints are removed from the scene, maintaining the
        integrity of the Maya environment and the user's project.

        Edge Cases:
            Deletes the first instance of an object with a name corresponding to "self.name" and "self.mirrored_name";
            therefore, if the users chooses to name other objects using the same naming convention it may delete
            their object instead of the joint.
        """
        mc.delete(self.name)
        print(f"\n{self.name} Joint has been deleted")
        if self.x2_coord is None:
            pass
        else:
            mc.delete(self.mirrored_name)  # Deletes the mirrored joint
        print(f"\n{self.mirrored_name} Joint has been deleted")

    # Calculates and creates a mirrored joint based on the original's position
    def create_mirrored_joint(self):
        """
        This method handles the logic required to mirror a joint across the appropriate axis.

        Calculates the coordinates for a mirrored joint based on the original joint's position and creates it.

        Stores mirrored joint inside the same instance as the original
        so the delete button can also remove the mirrored joint.

        Edge Cases:
            1. 3D model isn't at world origin — Requires the model to be at world origin.
            2. The absolute value of a joint's X and Z coordinates are equal which
               occurs when a joint is at a perfect 45° angle
        """
        if self.indicator_light is True:  # Joint exists
            if self.x2_coord is not None:  # Joint already mirrored
                print(f"\n{self.mirrored_name} already exists.")
            else:
                if self.x1_coord is None:  # Joint doesn't exist
                    print(f"\nThere is no {self.name} Joint to mirror\n")
                elif abs(self.x1_coord) > abs(self.z1_coord):
                    print(f"\nMirroring {self.name} Joint along the YZ Axis\n")
                    self.x2_coord = -1 * self.x1_coord
                    self.y2_coord = self.y1_coord
                    self.z2_coord = self.z1_coord
                elif abs(self.z1_coord) > abs(self.x1_coord):
                    print(f"\nMirroring {self.name} Joint along the XY Axis\n")
                    self.x2_coord = self.x1_coord
                    self.y2_coord = self.y1_coord
                    self.z2_coord = -1 * self.z1_coord
                    mc.select(clear=True)
                    mc.joint(name=self.mirrored_name, position=(self.x2_coord,
                                                                self.y2_coord,
                                                                self.z2_coord))
                else:
                    pass

    # Parents joints together based on specified pairings creating bones in Maya
    @staticmethod
    def create_joint_bones():
        """
        Iterates through a predefined list of joint pairs, where each pair consists of a
        parent joint and a child joint. Attempts to parent each child to its corresponding
        parent, effectively creating 'bones' in Maya.

        Includes error handling where the specified joints might not exist or have already
        been parented, ensuring the integrity of the skeletal hierarchy.

        Edge Cases:
            1. If a joint does not exist in the scene, the method skips the pairing to prevent errors.
            2. The method uses a try-except block to handle situations where Maya's parenting
               command might fail, such as when attempting to re-parent an already parented joint.

        Notes:
            1. Shoulder will be the child of the final Spine joint closest to the Neck.
            2. When adding additional parent-child pairs, write them as `["Parent", "Child"]`;
               ensuring the names match the Joint's corresponding `self.name` value.
        """
        joint_pairs = [
            ["Pelvis", "Hip"],
            ["Hip", "Knee"],
            ["Knee", "Ankle"],
            ["Ankle", "Ball_Of_Foot"],
            ["Ball_Of_Foot", "Toes"],
            ["Neck", "Head"],
            ["Shoulder", "Elbow"],
            ["Elbow", "Wrist"],
            ["Wrist", "Thumb_Base"],
            ["Thumb_Base", "Thumb_Middle"],
            ["Thumb_Middle", "Thumb_Distal"],
            ["Thumb_Distal", "Thumb_Tip"],
            ["Wrist", "Index_Finger_Base"],
            ["Index_Finger_Base", "Index_Finger_Middle"],
            ["Index_Finger_Middle", "Index_Finger_Distal"],
            ["Index_Finger_Distal", "Index_Finger_Tip"],
            ["Wrist", "Middle_Finger_Base"],
            ["Middle_Finger_Base", "Middle_Finger_Middle"],
            ["Middle_Finger_Middle", "Middle_Finger_Distal"],
            ["Middle_Finger_Distal", "Middle_Finger_Tip"],
            ["Wrist", "Thumb_Base"],
            ["Ring_Finger_Base", "Ring_Finger_Middle"],
            ["Ring_Finger_Middle", "Ring_Finger_Distal"],
            ["Ring_Finger_Distal", "Ring_Finger_Tip"],
            ["Wrist", "Pinky_Finger_Base"],
            ["Pinky_Finger_Base", "Pinky_Finger_Middle"],
            ["Pinky_Finger_Middle", "Pinky_Finger_Distal"],
            ["Pinky_Finger_Distal", "Pinky_Finger_Tip"],
            ["Pelvis", "Mirrored_Hip"],
            ["Mirrored_Hip", "Mirrored_Knee"],
            ["Mirrored_Knee", "Mirrored_Ankle"],
            ["Mirrored_Ankle", "Mirrored_Ball_Of_Foot"],
            ["Mirrored_Ball_Of_Foot", "Mirrored_Toes"],
            ["Mirrored_Neck", "Mirrored_Head"],
            ["Mirrored_Shoulder", "Mirrored_Elbow"],
            ["Mirrored_Elbow", "Mirrored_Wrist"],
            ["Mirrored_Wrist", "Mirrored_Thumb_Base"],
            ["Mirrored_Thumb_Base", "Mirrored_Thumb_Middle"],
            ["Mirrored_Thumb_Middle", "Mirrored_Thumb_Distal"],
            ["Mirrored_Thumb_Distal", "Mirrored_Thumb_Tip"],
            ["Mirrored_Wrist", "Mirrored_Index_Finger_Base"],
            ["Mirrored_Index_Finger_Base", "Mirrored_Index_Finger_Middle"],
            ["Mirrored_Index_Finger_Middle", "Mirrored_Index_Finger_Distal"],
            ["Mirrored_Index_Finger_Distal", "Mirrored_Index_Finger_Tip"],
            ["Mirrored_Wrist", "Mirrored_Middle_Finger_Base"],
            ["Mirrored_Middle_Finger_Base", "Mirrored_Middle_Finger_Middle"],
            ["Mirrored_Middle_Finger_Middle", "Mirrored_Middle_Finger_Distal"],
            ["Mirrored_Middle_Finger_Distal", "Mirrored_Middle_Finger_Tip"],
            ["Mirrored_Wrist", "Mirrored_Thumb_Base"],
            ["Mirrored_Ring_Finger_Base", "Mirrored_Ring_Finger_Middle"],
            ["Mirrored_Ring_Finger_Middle", "Mirrored_Ring_Finger_Distal"],
            ["Mirrored_Ring_Finger_Distal", "Ring_Finger_Tip"],
            ["Mirrored_Wrist", "Mirrored_Pinky_Finger_Base"],
            ["Mirrored_Pinky_Finger_Base", "Mirrored_Pinky_Finger_Middle"],
            ["Mirrored_Pinky_Finger_Middle", "Mirrored_Pinky_Finger_Distal"],
            ["Mirrored_Pinky_Finger_Distal", "Mirrored_Pinky_Finger_Tip"],
        ]

        # Parents Joints, excluding Spine
        for row in joint_pairs:
            try:  # Runs if the joint is an orphan
                if mc.objExists(f"{row[0]}"):  # Runs if the desired Parent Joint exists
                    if mc.objExists(f"{row[1]}"):  # Runs if the designed Child Joint exists
                        mc.parent(f"{row[1]}", f"{row[0]}")
            except RuntimeError:
                pass  # Ignoring error caused by joints already being parented

        time.sleep(time_sleep)

    # Sets up the UI layout for a row of joint control buttons.
    def create_button_row(self):
        """
        Creates a row layout in the UI consisting of joint control buttons,
        including indicators for joint status and buttons for joint operations.

        Sets up a row for each joint with a specific layout, including an indicator light,
        main action button, delete button, and help button.
        """
        mc.rowLayout(numberOfColumns=4, adjustableColumn=2)
        mc.button(self.indicator_label, label=orange_square_icon, enable=False, width=28, height=button_height)
        mc.button(label=self.name, command=lambda _: self.main_button(), width=28, height=button_height)
        mc.button(label=delete_icon, enable=True, width=28, height=button_height,
                  command=lambda _: self.delete_joint_button())
        mc.button(label="?", enable=False, width=28, height=button_height, command=lambda _: self.get_help())
        mc.setParent('..')  # Step back up to the parent layout