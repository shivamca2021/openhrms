/** @odoo-module **/
    import { UserMenu } from "@web/webclient/user_menu/user_menu";
    import { patch } from "@web/core/utils/patch";
    import { registry } from "@web/core/registry";

    const userMenuRegistry = registry.category("user_menuitems");

    //For remove menu:
    patch(UserMenu.prototype, "base_user_cuid.UserMenu", {
        setup() {
            this._super.apply(this, arguments);

            userMenuRegistry.remove("Remainders");
            userMenuRegistry.remove("Conversations");
            userMenuRegistry.remove("Activities");
           
        },
    });

