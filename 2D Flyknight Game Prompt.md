2D Flyknight Game Prompt

This game will be coded in Python using Pygame and other required libraries. The game is a 2D Top-Down Dungeon Crawler with procedurally generated dungeons. Dungeons will comprise several rooms, in which one of the 3 types of enemies will spawn, in their respective group size. The first dungeon will have about 6 rooms, and every dungeon after that will have more. You play as a FlyKnight, and can join up to 3 other players, meaning the game will be multiplayer, having it work cross computer and set up a lan connection between the players. Each player has an inventory that can hold 20 items, as well as allow them to see their character, equip armor, and equip weapons. Some weapons are one handed, meaning you can also equip a shield, but some are two handed, so you cannot equip a shield. Use left click to attack, and hold right click to use your shield if you have one equipped. When a hit is blocked, damage taken is reduced, and a bit of stamina is used. Attacking, blocking hits, and sprinting takes stamina. You cannot regenerate stamina while holding up a shield. Certain armor will reduce your stamina regeneration, but provide more protection. Each piece of armor from a set has the same stats, and each set has a Helmet, Chestplate, and Greaves. 

**Weapons and descriptions:**

- Sword

One handed weapon. Medium attack speed. Medium damage. Common drop. (Average range)

- Hammer 

Two handed weapon. Slow attack speed. Great damage. Rare drop. (This weapon has the SAME range as sword)

- Daggers

Two handed weapon. Fast attack speed. Medium damage. Rare drop. (This weapon has LESS range than sword)

- Spear

Two handed weapon. Slow attack speed. Medium damage. Rare drop. (this weapon has MORE range than sword)

**Shields:**

- Parrying Buckler

Light shield that doesn't block much damage but doesn't take much stamina when a hit is blocked.

- Soldier Board

Medium shield that blocks a medium amount of damage, and takes a medium amount of stamina when a hit is blocked.

- Tower Shield

Large shield that blocks a large amount of damage, and takes a large amount of stamina when a hit is blocked.

**Armor and descriptions:**

- Knight set

The basic armor set that you start with. Medium all around.

- Samurai set

A rare armor set dropped by wasps. Has high damage reduction but greatly reduces stamina regeneration.

- Ranger set

A rare armor set dropped by ants. Has low damage reduction but barely reduces stamina regeneration.

**Enemy types and descriptions:**

- Larva

Small size, slow movement speed, with little hp, they spawn in large groups and jump at you when you are in their line of sight. Otherwise, they slowly move randomly around. Very common enemy.

- Ant

Medium size, medium movement speed, and medium hp, they spawn in groups of 1-2 and use melee attacks to try to kill you. Rarely, they may spawn with a bow. If they do not have a bow, they randomly walk around until you are in their radius. If they do have a bow, they wait in place until you enter their radius. Common enemy.

- Wasp

Slightly larger than Ants, slightly faster than Ants, and with a large amount of hp, they spawn by themselves and use melee attacks to kill you. They move randomly around when you are not in their radius, but tend to stay near the same spot. Rare enemy.