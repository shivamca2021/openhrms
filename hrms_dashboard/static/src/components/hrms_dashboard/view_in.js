/** @odoo-module **/
import { registry } from  "@web/core/registry"
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";

class HrAttendanceListController extends ListController {
    setup() {
        super.setup()
        console.log("This is Res Partner Controller List...")
        this.action = useService("action")
    }
    openSalesView() {
        console.log("Request New Leave")
        this.action.doAction({
            type:"ir.actions.act_window",
            name:"New Leave Request",
            res_model:"hr.leave",
            views:[[false, "form"]]
        })
    }    
} 

export const hrattendListView = {
    ...listView,
    Controller: HrAttendanceListController,
    buttonTemplate: "hrms_dashboard.owl_listview_button",   
}
registry.category("views").add("button_onlist_view",hrattendListView)