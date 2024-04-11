# --------------------------------------------------------------------------------
# Script Name: AutoRig Script
# Description: This script is used to streamline the rigging process for bi-pedal characters in Maya.
#              It builds upon the Joint class to specifically manage spine joints
#              and their interactions in Maya. It includes functionality for creating,
#              deleting, and adjusting spine joints, along with a comprehensive UI for rigging operations.
# Author: Kai Mallari
# Created: February 2024
# --------------------------------------------------------------------------------

import maya.cmds as mc
import time
from autoRig.class_Joint import Joint
from autoRig.class_Joint import orange_square_icon
from autoRig.class_Joint import button_height
from autoRig.class_Joint import delete_icon

time_sleep: float = 0.05  # Prevents program from skipping steps by running too fast

spine_joints = []  # Used by `Spine.create_spine()` for dynamically creating instances of the Spine Joint class


# Extends the Joint class to manage spine-specific joint operations and attributes
class Spine(Joint):
    def __init__(self, name, url):
        """
        Initializes a Spine instance with name, URL, and default joint count settings.

        Inherits from the Joint class and adds spine-specific attributes, including a default
        joint count and a method to track the maximum index for spine joints, aiding in
        their management and hierarchical structuring in Maya.

        Parameters:
            name (str): Name of the spine joint, adhering to naming conventions.
            url (str): URL for documentation or relevant information about the spine joint.
            """
        super().__init__(name, url)
        self.joint_count: int = 3  # Desired number of spine joints for the rig; set as default but adjusted by user.
        self.max_index: int = self.joint_count - 1  # Used to find the spine joint closest to the neck; parents the spine with the neck and shoulders

    # Triggers spine creation process, validating prerequisites
    def create_spine_button(self):
        """
        Checks conditions and initiates the creation of spine joints when triggered by the UI.

        This method serves as a preliminary check to ensure that the necessary prerequisites,
        such as the existence and readiness of neck and pelvis joints, are met before proceeding
        to create the spine. It provides user feedback if conditions are not met or confirms
        the initiation of spine creation.

        Uses `indicator_light` from the to prevent duplicate spine creations and ensure that
        spine joints are created in a controlled and error-free manner.
        """
        if self.indicator_light is True:
            print("\nSpine already exists")
        else:
            if neck.indicator_light and pelvis.indicator_light is not True:
                print("\nPlease finish creating the Pelvis and Neck Joints before creating the Spine")
            else:
                print("\nCreating Spine")
                self.create_spine()

    # Dynamically creates and evenly distributes spine joints between the neck and pelvis
    def create_spine(self):
        """
        Dynamically creates and positions spine joints based on the user-defined joint count
        and the positions of the neck and pelvis joints.

        This method calculates the positions for spine joints to be evenly distributed
        between the neck and pelvis, creating a realistic spinal structure. It ensures
        spine joints are created only if the pelvis and neck joints exist and are properly configured.

        Globals:
            spine_joints (list): Updated with newly created spine joint instances.
        """
        global spine_joints
        spine_joints = [Joint(f"Spine_{i}", self.help_url) for i in
                        range(self.joint_count)]  # Initialize spine joint instances

        # Calculate distances for even spacing between neck and pelvis joints
        joints_spacer = self.joint_count + 1
        x_distance = (neck.x1_coord - pelvis.x1_coord) / joints_spacer
        y_distance = (neck.y1_coord - pelvis.y1_coord) / joints_spacer
        z_distance = (neck.z1_coord - pelvis.z1_coord) / joints_spacer

        spine_coords = [], [], []  # Store coordinates for each spine joint

        # Populate X coordinates for spine joints, ensuring even spacing
        spine_count_placeholder = self.joint_count
        coords = pelvis.x1_coord
        while spine_count_placeholder > 0:
            coords += x_distance
            spine_coords[0].append(coords)
            spine_count_placeholder -= 1

        # Repeat the process for Y and Z coordinates
        spine_count_placeholder = self.joint_count
        coords = pelvis.y1_coord
        while spine_count_placeholder > 0:
            coords += y_distance
            spine_coords[1].append(coords)
            spine_count_placeholder -= 1

        spine_count_placeholder = self.joint_count
        coords = pelvis.z1_coord
        while spine_count_placeholder > 0:
            coords += z_distance
            spine_coords[2].append(coords)
            spine_count_placeholder -= 1

        mc.select(clear=True)  # Clear selection to prevent unintended parenting

        # Assign calculated coordinates to spine joints and create them in Maya
        spine_index = 0
        for i in range(self.joint_count):
            spine_joints[i].x1_coord = spine_coords[0][spine_index]
            spine_joints[i].y1_coord = spine_coords[1][spine_index]
            spine_joints[i].z1_coord = spine_coords[2][spine_index]
            mc.joint(name=spine_joints[i].name,
                     position=(spine_joints[i].x1_coord, spine_joints[i].y1_coord, spine_joints[i].z1_coord))
            mc.select(clear=True)  # Ensure each joint is created independently without parenting
            spine_index += 1
        self.indicator_light_on()  # Update the UI to reflect spine creation

    # Unparents spine joints from Neck, Shoulders, and each other
    def unparent_spine(self):
        """
        Unparents spine joints from the Neck, Shoulders, and each other to ensure
        they can be safely modified or deleted.

        This function checks if the Spine joints are currently parented to the
        Neck or Shoulders and unparents them if necessary. It also sequentially unparents
        each Spine joint from any other joints to avoid deletion issues when updating the Spine.

        Using Try/Except to prevent Runtime Error which occurs when trying
        to unparent a relationship that doesn't exist.
        """
        # Check if the last spine joint is parented and unparent Neck and Shoulders
        if mc.listRelatives(f"Spine_{self.max_index}", parent=True):
            try:
                mc.parent("Neck", world=True)  # Attempt to unparent the Neck
            except RuntimeError:
                pass  # Ignore error if Neck is not parented

            # Check and unparent both Shoulder and Mirrored_Shoulder
            try:
                if mc.objExists("Shoulder"):
                    mc.parent("Shoulder", world=True)  # Unparent Shoulder
            except RuntimeError:
                pass  # Ignore error if Shoulder is not parented

            try:
                if mc.objExists("Mirrored_Shoulder"):
                    mc.parent("Mirrored_Shoulder", world=True)  # Unparent Mirrored_Shoulder
            except RuntimeError:
                pass  # Ignore error if Mirrored_Shoulder is not parented

            # Sequentially unparent each spine joint, starting from the top
            spine_parent_index = self.max_index
            while spine_parent_index >= 0:
                mc.parent(f"Spine_{spine_parent_index}", world=True)  # Unparent the joint
                spine_parent_index -= 1

    # Initiates the deletion process for spine joints
    def delete_spine_button(self):
        """
        Triggers the process to delete existing spine joints through the UI button.

        Uses `time_sleep` to ensure the UI updates appropriately after deleting each spine joint.
        """
        if self.indicator_light is False:
            print("\nThere is no Spine to delete")
        else:
            self.unparent_spine()
            time.sleep(time_sleep)
            self.indicator_light_off()
            self.delete_spine()

    # Deletes all spine joints from the scene
    def delete_spine(self):
        """
        Iterates through the list of spine joints, deleting each one from the scene.

        Typically called after unparenting the spine joints to ensure a clean removal
        without leaving any orphaned joints.
        """
        for i in range(self.joint_count):
            mc.delete(f"Spine_{i}")  # Deletes the joint
            print(f"\nClearing spine_joints[{i}]")
            spine_joints[i] = None

    # Updates the max index for spine joints based on the current count
    def update_spine_max_index(self):
        """
        Updates the maximum index value for spine joints.

        This function is crucial for functions that rely on the index of the last spine joint,
        ensuring they operate on up-to-date information, especially after adding or removing spine joints.
        """
        self.max_index = self.joint_count - 1

    # Adds a spine joint to the rig
    def add_spine_button(self):
        """
        Increments the number of spine joints, or if spine joints already exist, deletes the current spine,
        increments the number of spine joints, and then recreates the spine to reflect the new count.
        """
        if self.indicator_light is False:
            self.add_spine()
        else:
            self.delete_spine_button()
            self.add_spine()
            self.create_spine_button()

    # Removes a spine joint from the rig
    def remove_spine_button(self):
        """
        Decrements the number of spine joints, or if spine joints already exist, deletes the current spine,
        decrements the number of spine joints, and then recreates the spine to reflect the new count.
        """
        if self.joint_count > 1:
            if self.indicator_light is False:
                self.remove_spine()
            else:
                self.delete_spine_button()
                self.remove_spine()
                self.create_spine_button()

    # Increments the spine joint count by one
    def add_spine(self):
        """
        Adds another spine joint to the rig and updates the `max_index` to reflect the new count.
        """
        self.joint_count += 1
        self.update_spine_max_index()

    # Decrements the spine joint count by one, ensuring a minimum count of one
    def remove_spine(self):
        """
        Decreases the count of spine joints in the rig configuration, with a lower limit of at least one joint.
        """
        self.joint_count -= 1
        self.update_spine_max_index()

    # Resets the spine joint count to the default value through the UI
    def reset_spine_button(self):
        """
        Resets the spine joint count to a default value (typically 3) via a UI button.

        This function provides a quick way to revert the spine configuration to a
        standard setup with a default number of joints.

        It handles the resetting process by first checking if any spine joints exist and need deletion,
        then sets the `joint_count` to the default, and updates the UI and rig accordingly.
        """
        if self.indicator_light is False:
            self.reset_spine()
        else:
            self.delete_spine_button()
            self.reset_spine()
            self.create_spine_button()

    # Resets the spine joint count to the default value
    def reset_spine(self):
        """
        Directly resets the spine joint count to a default value, typically 3, without UI interaction.

        Used for programmatically resetting the spine configuration to a standard number of joints,
        this function updates the `joint_count` attribute to the default and adjusts the `max_index` to match.

        It's useful for scripts or processes that require resetting the rig to a known state.
        """
        self.joint_count = 3
        self.update_spine_max_index()

    # Parents spine joints and connects them to the Pelvis and Neck
    def create_spine_bones(self):
        """
        Parents spine joints together and attaches the spine to the Pelvis and Neck joints.

        Handles parenting in a specific order to maintain the rig's integrity and includes
        checks to ensure the necessary joints exist before attempting to parent them.
        """
        # Parent Spine Joints
        if not mc.objExists("Spine_0"):
            print("\nSpine doesn't exist")
        else:
            # Parent Spine Joints using the consecutive index numbers from 0 until the max index.
            for i in range(self.joint_count):
                if i < self.max_index:
                    try:
                        mc.parent(f"Spine_{i + 1}", f"Spine_{i}")
                    except RuntimeError:
                        pass  # Ignoring error caused by joints already being parented

            time.sleep(time_sleep)

            # Parent Spine to the Pelvis
            if not mc.objExists("Pelvis"):
                print("\nPelvis doesn't exist")
            else:
                try:
                    mc.parent(f"Spine_0", "Pelvis")
                except RuntimeError:
                    pass  # Ignoring error caused by joints already being parented

            time.sleep(time_sleep)

            # Parent Neck to the Spine
            if not mc.objExists("Neck"):
                print("\nNeck doesn't exist")
            else:
                try:
                    mc.parent("Neck", f"Spine_{self.max_index}")
                except RuntimeError:
                    pass  # Ignoring error caused by joints already being parented

            time.sleep(time_sleep)

            # Parent Shoulder to the Spine
            if not mc.objExists("Shoulder"):
                print("\nShoulder doesn't exist")
            else:
                try:
                    mc.parent("Shoulder", f"Spine_{self.max_index}")
                except RuntimeError:
                    pass  # Ignoring error caused by joints already being parented

            time.sleep(time_sleep)

            # Parent Mirrored_Shoulder to the Spine
            if not mc.objExists("Mirrored_Shoulder"):
                print("\nShoulder doesn't exist")
            else:
                try:
                    mc.parent("Mirrored_Shoulder", f"Spine_{self.max_index}")
                except RuntimeError:
                    pass  # Ignoring error caused by joints already being parented


# Triggers the process of creating bones
def create_bone_button():
    """
    Calls the functions to parent joints together, creating bones in Maya.
    """
    spine.create_spine_bones()
    time.sleep(time_sleep)
    Joint.create_joint_bones()


# Initiates the mirroring process for arm and leg joints
def mirror_button():
    """
    Executes the joint mirroring operation for all specified arm and leg joints,
    including fingers, iterating through each joint.
    """
    # Mirror Arm
    shoulder.create_mirrored_joint()
    elbow.create_mirrored_joint()
    wrist.create_mirrored_joint()

    # Mirror Thumb
    thumb_base.create_mirrored_joint()
    thumb_middle.create_mirrored_joint()
    thumb_distal.create_mirrored_joint()
    thumb_tip.create_mirrored_joint()

    # Mirror Index Finger
    index_base.create_mirrored_joint()
    index_middle.create_mirrored_joint()
    index_distal.create_mirrored_joint()
    index_tip.create_mirrored_joint()

    # Mirror Middle Finger
    middle_base.create_mirrored_joint()
    middle_middle.create_mirrored_joint()
    middle_distal.create_mirrored_joint()
    middle_tip.create_mirrored_joint()

    # Mirror Ring Finger
    ring_base.create_mirrored_joint()
    ring_middle.create_mirrored_joint()
    ring_distal.create_mirrored_joint()
    ring_tip.create_mirrored_joint()

    # Mirror Pinky Finger
    pinky_base.create_mirrored_joint()
    pinky_middle.create_mirrored_joint()
    pinky_distal.create_mirrored_joint()
    pinky_tip.create_mirrored_joint()

    # Mirror Leg
    hip.create_mirrored_joint()
    knee.create_mirrored_joint()
    ankle.create_mirrored_joint()
    ball_of_foot.create_mirrored_joint()
    toes.create_mirrored_joint()


# All the class instances created here
spine = Spine("Spine", "www.example.com")

pelvis = Joint("Pelvis", "www.example.com")
neck = Joint("Neck", "www.example.com")
head = Joint("Head", "www.example.com")

shoulder = Joint("Shoulder", "www.example.com")
elbow = Joint("Elbow", "www.example.com")
wrist = Joint("Wrist", "www.example.com")

thumb_base = Joint("Thumb_Base", "www.example.com")
thumb_middle = Joint("Thumb_Middle", "www.example.com")
thumb_distal = Joint("Thumb_Distal", "www.example.com")
thumb_tip = Joint("Thumb_Tip", "www.example.com")

index_base = Joint("Index_Finger_Base", "www.example.com")
index_middle = Joint("Index_Finger_Middle", "www.example.com")
index_distal = Joint("Index_Finger_Distal", "www.example.com")
index_tip = Joint("Index_Finger_Tip", "www.example.com")

middle_base = Joint("Middle_Finger_Base", "www.example.com")
middle_middle = Joint("Middle_Finger_Middle", "www.example.com")
middle_distal = Joint("Middle_Finger_Distal", "www.example.com")
middle_tip = Joint("Middle_Finger_Tip", "www.example.com")

ring_base = Joint("Ring_Finger_Base", "www.example.com")
ring_middle = Joint("Ring_Finger_Middle", "www.example.com")
ring_distal = Joint("Ring_Finger_Distal", "www.example.com")
ring_tip = Joint("Ring_Finger_Tip", "www.example.com")

pinky_base = Joint("Pinky_Finger_Base", "www.example.com")
pinky_middle = Joint("Pinky_Finger_Middle", "www.example.com")
pinky_distal = Joint("Pinky_Finger_Distal", "www.example.com")
pinky_tip = Joint("Pinky_Finger_Tip", "www.example.com")

hip = Joint("Hip", "www.example.com")
knee = Joint("Knee", "www.example.com")
ankle = Joint("Ankle", "www.example.com")
ball_of_foot = Joint("Ball_Of_Foot", "www.example.com")
toes = Joint("Toes", "www.example.com")


# UI Code Starts Here -- Needs to be inside this document because it calls functions from the Joint and Spine instances

# Creates a header label for UI sections
def create_section_header(label):
    """
    Generates a text label in the UI to serve as a header for a new section.

    Parameters:
        label (str): The text displayed as the header.
    """
    mc.text(label=label, align='center', font='boldLabelFont', height=30)


# Initializes a collapsible dropdown menu for organizing related UI elements
def create_dropdown_menu(label):
    """
    Creates a frame layout that functions as a dropdown menu, grouping related UI elements under a common label.

    Organizes the UI by allowing users to expand or collapse sections, keeping the interface clean and manageable,
    especially when dealing with numerous controls.

    Parameters:
        label (str): The label for the dropdown menu.
    """
    mc.frameLayout(label=label, collapsable=True, collapse=True)
    mc.columnLayout(adjustableColumn=True)


# Creates the main autoRig UI window with all controls and layouts
def create_autoRig_UI():
    """
    Builds the main user interface for the autoRig tool, assembling all controls, buttons, and layout structures,
    organizing it into sections and dropdown menus for different rigging operations.
    """
    if mc.window("autoRig_main_window", exists=True):  # Prevents multiple copies of the UI from opening
        mc.deleteUI("autoRig_main_window", window=True)

    mc.window("autoRig_main_window", title="autoRig", width=250, height=850, sizeable=False)

    # Creates a scrolling bar for when every dropdown menu item is open otherwise they are inaccessible
    scroll_layout = mc.scrollLayout(verticalScrollBarThickness=255)
    main_layout = mc.columnLayout(width=230, adjustableColumn=True)

    # Center Section
    create_section_header("Set Center Selections")
    pelvis.create_button_row()
    neck.create_button_row()
    head.create_button_row()

    # Arm Section
    create_section_header("Set Arm Selections")
    shoulder.create_button_row()
    elbow.create_button_row()
    wrist.create_button_row()

    # Add Separator without Line
    mc.separator(style="none", height=10)

    # Finger Section
    create_section_header("Set Finger Selections")

    create_dropdown_menu("View Thumb Selections")
    thumb_base.create_button_row()
    thumb_middle.create_button_row()
    thumb_distal.create_button_row()
    thumb_tip.create_button_row()

    # Return to main column hierarchy
    mc.setParent('..')
    mc.setParent('..')

    create_dropdown_menu("View Index Finger Selections")
    index_base.create_button_row()
    index_middle.create_button_row()
    index_distal.create_button_row()
    index_tip.create_button_row()

    # Return to main column hierarchy
    mc.setParent('..')
    mc.setParent('..')

    create_dropdown_menu("View Middle Finger Selections")
    middle_base.create_button_row()
    middle_middle.create_button_row()
    middle_distal.create_button_row()
    middle_tip.create_button_row()

    # Return to main column hierarchy
    mc.setParent('..')
    mc.setParent('..')

    create_dropdown_menu("View Ring Finger Selections")
    ring_base.create_button_row()
    ring_middle.create_button_row()
    ring_distal.create_button_row()
    ring_tip.create_button_row()

    # Return to main column hierarchy
    mc.setParent('..')
    mc.setParent('..')

    create_dropdown_menu("View Pinky Finger Selections")
    pinky_base.create_button_row()
    pinky_middle.create_button_row()
    pinky_distal.create_button_row()
    pinky_tip.create_button_row()

    # Return to main column hierarchy
    mc.setParent('..')
    mc.setParent('..')

    # Leg Section
    create_section_header("Set Leg Selections")

    create_dropdown_menu("View Leg Selections")
    hip.create_button_row()
    knee.create_button_row()
    ankle.create_button_row()
    ball_of_foot.create_button_row()
    toes.create_button_row()

    # Return to main column hierarchy
    mc.setParent('..')
    mc.setParent('..')

    # Add Separator
    mc.separator(height=20)

    # Adjust Joints Section
    create_section_header("Adjust Joints")

    # Dropdown Toggle - Adjust Spine Joints
    create_dropdown_menu("Adjust Spine Joints")

    # Create Spine Joints Button -- Creates a row of buttons including an indicator, selector, and help button.
    mc.rowLayout(numberOfColumns=4, adjustableColumn=2)
    mc.button(spine.indicator_label, label=orange_square_icon, enable=False, width=28, height=button_height)
    mc.button(label="Create Spine", height=button_height, command=lambda _: spine.create_spine_button())
    mc.button(label=delete_icon, enable=True, width=28, height=button_height,
              command=lambda _: spine.delete_spine_button())
    mc.button(label="?", enable=False, width=28, height=button_height, command=lambda _: spine.get_help())
    mc.setParent('..')  # Step back up to the parent layout

    # Add / Remove Spine Joints Button
    mc.rowLayout(numberOfColumns=2)
    mc.button(label="Add Joint", height=button_height, width=115, command=lambda _: spine.add_spine_button())
    mc.button(label="Remove Joint", height=button_height, width=115, command=lambda _: spine.remove_spine_button())
    mc.setParent('..')

    # Reset Spine Joints Button
    mc.rowLayout(numberOfColumns=2, adjustableColumn=1)
    mc.button(label="Reset Spine Joint Quantity", height=button_height, command=lambda _: spine.reset_spine_button())
    mc.button(label="?", enable=False, width=28, height=button_height)
    mc.setParent('..')

    # Return to main column hierarchy
    mc.setParent('..')
    mc.setParent('..')

    # Mirror Button
    mc.rowLayout(numberOfColumns=2, adjustableColumn=1)
    mc.button(label="Mirror Arm and Leg", height=button_height, command=lambda _: mirror_button())
    mc.button(label="?", enable=False, width=28, height=button_height, command=lambda _: webbrowser.open("www.example.com"))
    mc.setParent('..')

    # Add Separator
    mc.separator(height=20)

    # Finishing Section
    create_section_header("Finish Rigging")

    # Create Bones Button
    mc.rowLayout(numberOfColumns=2, adjustableColumn=1)
    mc.button(label="Create Bones", height=button_height, command=lambda _: create_bone_button())
    mc.button(label="?", enable=False, width=28, height=button_height, command=lambda _: webbrowser.open("www.example.com"))
    mc.setParent('..')
    mc.setParent('..')

    # Add Separator
    mc.separator(height=20)

    # When active, display UI
    mc.showWindow("autoRig_main_window")


# Entry point for creating and displaying the autoRig UI
create_autoRig_UI()
