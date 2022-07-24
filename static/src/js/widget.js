odoo.define('generate_purchase_order.widget', function (require) {
    var ListRenderer = require('web.ListRenderer');
    var registry = require('web.field_registry');
    var relational = require('web.relational_fields');

    var Selection = relational.FieldSelection.extend({
        init: function () {
            this._super.apply(this, arguments);
        },
        _renderReadonly: function () {
            this.$el.html(function () {
                var result = '';
                result =
                    '<div style="text-align: center;">' +
                    '<i class="fa fa-refresh" style="color: #7c7bad; font-size: 20px;"/>' +
                    '</div>';
                return result
            });
        }
    });
    registry.add('purchase_selection', Selection);

    return Selection
});