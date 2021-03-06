/* ----------------------------------------------------------------------
 * Numenta Platform for Intelligent Computing (NuPIC)
 * Copyright (C) 2015, Numenta, Inc.  Unless you have purchased from
 * Numenta, Inc. a separate commercial license for this software code, the
 * following terms and conditions apply:
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see http://www.gnu.org/licenses.
 *
 * http://numenta.org/licenses/
 * ---------------------------------------------------------------------- */

describe('YOMP Backbone.View: Welcome', function() {

    var api =   new YOMPAPI({ apiKey: 'xxx' }),
        view =  new YOMPUI.WelcomeView({ api: api });

    it('should construct simply', function() {
        expect(view).to.be.an('object');
    });

    it('should affect page title', function() {
        expect(document.title).to.contain(YOMPUI.msgs('welcome-tmpl').title);
    });

});
