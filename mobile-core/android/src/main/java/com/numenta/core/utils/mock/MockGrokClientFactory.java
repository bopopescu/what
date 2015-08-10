/*
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
 *
 */

package com.numenta.core.utils.mock;

import com.numenta.core.service.YOMPClient;
import com.numenta.core.service.YOMPClientFactory;

import java.net.MalformedURLException;

/**
 * Mock factory returning a single {@link YOMPClient}
 *
 * @see MockYOMPClient
 */
public class MockYOMPClientFactory implements YOMPClientFactory {

    private YOMPClient _YOMPClient;

    public MockYOMPClientFactory() {

    }

    public MockYOMPClientFactory(YOMPClient YOMPClient) {
        _YOMPClient = YOMPClient;
    }

    @Override
    public YOMPClient createClient(String serverUrl, String pass) throws MalformedURLException {
        return _YOMPClient;
    }
}
