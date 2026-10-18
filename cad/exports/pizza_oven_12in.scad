// OpenSCAD Parametric Neapolitan Pizza Oven Model
// Generated automatically by cad/model_generator.py

$fn = 60;

// Master Parameters
stone_width = 330.0;
stone_depth = 330.0;
stone_thickness = 15.0;

chamber_width = 350.0;
chamber_depth = 440.0;
dome_apex_height = 190.0;
inner_sheet_t = 1.5;

mouth_height = 119.7;
mouth_width = 308.0;

insulation_cavity = 27.0;
outer_sheet_t = 1.2;
outer_width = 407.0;
outer_depth = 482.0;
outer_height = 244.0;

flue_diameter = 100.0;
chimney_collar_h = 65.0;
leg_height = 135.0;

module baking_stone() {
    color([0.85, 0.75, 0.65])
    translate([-stone_width/2, 15, 0])
    cube([stone_width, stone_depth, stone_thickness]);
}

module inner_dome() {
    color([0.85, 0.88, 0.90])
    difference() {
        // Outer arch
        translate([0, 0, 0])
        rotate([-90, 0, 0])
        linear_extrude(chamber_depth)
        scale([chamber_width/2, dome_apex_height])
        circle(r=1);

        // Hollow interior
        translate([0, -1, 0])
        rotate([-90, 0, 0])
        linear_extrude(chamber_depth + 2)
        scale([(chamber_width/2) - inner_sheet_t, dome_apex_height - inner_sheet_t])
        circle(r=1);

        // Flat bottom floor cut
        translate([-chamber_width, -1, -dome_apex_height])
        cube([2 * chamber_width, chamber_depth + 2, dome_apex_height]);

        // Front mouth opening (Neapolitan 63% rule)
        translate([-mouth_width/2, -1, 0])
        cube([mouth_width, 10, mouth_height]);

        // Flue chimney exhaust hole
        translate([0, 45, dome_apex_height - 20])
        cylinder(r=flue_diameter/2, h=50);
    }
}

module outer_shroud() {
    color([0.2, 0.2, 0.22, 0.85])
    difference() {
        translate([0, -10, -12])
        rotate([-90, 0, 0])
        linear_extrude(outer_depth)
        scale([outer_width/2, outer_height])
        circle(r=1);

        // Inner cavity
        translate([0, -12, -12])
        rotate([-90, 0, 0])
        linear_extrude(outer_depth + 4)
        scale([(outer_width/2) - outer_sheet_t, outer_height - outer_sheet_t])
        circle(r=1);

        // Bottom cut
        translate([-outer_width, -15, -outer_height - 12])
        cube([2 * outer_width, outer_depth + 10, outer_height]);

        // Front face opening
        translate([-mouth_width/2 - 10, -15, -12])
        cube([mouth_width + 20, 20, mouth_height + 25]);

        // Flue collar penetration
        translate([0, 45, outer_height - 30])
        cylinder(r=(flue_diameter/2) + 1, h=60);
    }
}

module chimney_collar() {
    color([0.9, 0.9, 0.92])
    translate([0, 45, outer_height - 12])
    difference() {
        cylinder(r=flue_diameter/2, h=chimney_collar_h);
        translate([0, 0, -1])
        cylinder(r=(flue_diameter/2) - 1.5, h=chimney_collar_h + 2);
    }
}

module folding_legs() {
    color([0.7, 0.7, 0.72])
    for (lx = [-outer_width/2, outer_width/2 - 2]) {
        for (ly = [30, outer_depth - 40]) {
            translate([lx, ly, -12 - leg_height])
            cube([2.0, 35.0, leg_height]);
        }
    }
}

// Full Assembly
baking_stone();
inner_dome();
outer_shroud();
chimney_collar();
folding_legs();
