#!/bin/bash

# Create entrypoint script
cat >lambda-entrypoint.sh <<-EOF
#!/bin/bash

local_runtime_interface=/usr/local/bin/aws-lambda-rie

if [ \$# -ne 1 ]; then
    echo "entrypoint requires the handler name to be the first argument" 1>&2
    exit 142
fi

if [ -z "\${AWS_LAMBDA_RUNTIME_API}" ]; then
    if [ -e \${local_runtime_interface} ];then
        exec /usr/local/bin/aws-lambda-rie /usr/bin/python3 -m awslambdaric "\$1"
    else
        echo "No local aws-lambda-rie interface found"
        echo "For details see: https://github.com/aws/aws-lambda-runtime-interface-emulator?tab=readme-ov-file#installing"
        exit 143
    fi
else
    exec /usr/bin/python3 -m awslambdaric "\$1"
fi
EOF
chmod 755 lambda-entrypoint.sh
